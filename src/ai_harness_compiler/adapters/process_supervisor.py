"""Bounded JSON worker subprocess. Trusted worker code; this is not a security sandbox."""

import json
import os
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Any

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.supervised_transport import TransportLimitsV1, TransportReceiptV1


@dataclass(frozen=True)
class WorkerOutcome:
    receipt: TransportReceiptV1
    response: str | None


def invoke_json_worker(
    command: list[str],
    payload: dict[str, Any],
    *,
    cwd: Path,
    limits: TransportLimitsV1,
    session_deadline: float,
    index: int,
) -> WorkerOutcome:
    """Send work only after containment is established; always clean the owned tree.

    The caller supplies a trusted fixed command, never model-produced instructions.
    No shell, retries, raw diagnostics, transcript persistence or network defaults.
    """
    limits = TransportLimitsV1.model_validate(limits.model_dump())
    if index not in {1, 2} or not command:
        raise ValueError("Invalid worker invocation")
    started = monotonic()
    granted = min(
        float(limits.call_timeout_seconds),
        session_deadline - started - limits.cleanup_timeout_seconds,
    )
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n"
    fields: dict[str, Any] = dict(
        index=index,
        payload_sha256=canonical_project_digest(payload),
        command_sha256=canonical_project_digest({"argv": command}),
        granted_seconds=max(0.0, granted),
        elapsed_seconds=0.0,
        containment="none",
        root_reaped=False,
        tree_termination_requested=False,
        status="failed",
        failure_code="session-budget" if granted <= 0 else "input-limit",
    )
    if granted <= 0 or len(encoded) > limits.max_input_bytes:
        fields["elapsed_seconds"] = monotonic() - started
        return WorkerOutcome(TransportReceiptV1.model_validate(fields), None)
    process: subprocess.Popen[bytes] | None = None
    job: Any = None
    output = bytearray()
    overflow = threading.Event()
    io_error = threading.Event()
    threads: list[threading.Thread] = []
    response = None
    try:
        fields["failure_code"] = "containment-failed"
        if os.name == "nt":
            from ai_harness_compiler.adapters.windows_process_job import WindowsProcessJob

            job = WindowsProcessJob()
        fields["failure_code"] = "spawn-failed"
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
            start_new_session=os.name != "nt",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
        fields["worker_pid"] = process.pid
        fields["failure_code"] = "containment-failed"
        if job is not None:
            job.attach(process.pid)
            fields["containment"] = "windows-job"
        else:
            fields["containment"] = "posix-session"
        fields["failure_code"] = "call-timeout"
        if monotonic() >= started + granted:
            raise TimeoutError("WORKER_STARTUP_EXHAUSTED_BUDGET")
        assert process.stdout is not None and process.stdin is not None
        reader_stream, writer_stream = process.stdout, process.stdin

        def read() -> None:
            try:
                while chunk := reader_stream.read(65536):
                    if len(output) + len(chunk) > limits.max_output_bytes:
                        overflow.set()
                        return
                    output.extend(chunk)
            except (OSError, ValueError):
                io_error.set()

        def write() -> None:
            try:
                writer_stream.write(encoded)
                writer_stream.close()
            except (OSError, ValueError):
                io_error.set()

        threads = [
            threading.Thread(target=read, daemon=True),
            threading.Thread(target=write, daemon=True),
        ]
        for thread in threads:
            thread.start()
        fields["failure_code"] = "call-timeout"
        deadline = started + granted
        while monotonic() < deadline and not overflow.is_set():
            try:
                process.wait(timeout=min(0.05, max(0.001, deadline - monotonic())))
                # EOF may depend on descendants: join only within call deadline.
                for thread in threads:
                    thread.join(timeout=max(0.0, deadline - monotonic()))
                if any(t.is_alive() for t in threads):
                    break
                if monotonic() > deadline:
                    break
                fields["failure_code"] = "worker-failed"
                if process.returncode != 0 or io_error.is_set():
                    break
                fields["failure_code"] = "invalid-output"
                envelope = json.loads(output)
                if (
                    not isinstance(envelope, dict)
                    or set(envelope) != {"response"}
                    or not isinstance(envelope["response"], str)
                ):
                    break
                response = envelope["response"]
                parsed = json.loads(response)
                if not isinstance(parsed, dict):
                    response = None
                    break
                if monotonic() > deadline:
                    response = None
                    fields["failure_code"] = "call-timeout"
                    break
                fields["response_sha256"] = canonical_project_digest(parsed)
                fields["failure_code"] = None
                break
            except subprocess.TimeoutExpired:
                continue
        if overflow.is_set():
            fields["failure_code"] = "output-limit"
    except Exception:
        # Preserve only the stage code; worker/OS messages may contain private data.
        pass
    finally:
        cleanup_deadline = min(session_deadline, monotonic() + limits.cleanup_timeout_seconds)
        if job is not None:
            closed = job.close()
            fields["tree_termination_requested"] = closed and fields["containment"] == "windows-job"
        elif (
            sys.platform != "win32"
            and process is not None
            and fields["containment"] == "posix-session"
        ):
            try:
                os.killpg(process.pid, signal.SIGKILL)
                fields["tree_termination_requested"] = True
            except ProcessLookupError:
                fields["tree_termination_requested"] = True  # Owned group already gone.
            except OSError:
                pass
        if process is not None:
            if process.poll() is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            try:
                process.wait(timeout=max(0.001, cleanup_deadline - monotonic()))
                fields.update(root_reaped=True, exit_code=process.returncode)
            except subprocess.TimeoutExpired:
                pass
            for thread in threads:
                thread.join(timeout=max(0.0, cleanup_deadline - monotonic()))
            if not any(t.is_alive() for t in threads):
                if process.stdout:
                    process.stdout.close()
                if process.stdin and not process.stdin.closed:
                    process.stdin.close()
            if (
                not fields["root_reaped"]
                or not fields["tree_termination_requested"]
                or any(t.is_alive() for t in threads)
            ):
                fields["failure_code"] = fields["failure_code"] or "cleanup-failed"
        elapsed = monotonic() - started
        if monotonic() > session_deadline and fields["failure_code"] is None:
            fields["failure_code"] = "session-budget"
        fields["elapsed_seconds"] = elapsed
        fields["status"] = "succeeded" if fields["failure_code"] is None else "failed"
    receipt = TransportReceiptV1.model_validate(fields)
    return WorkerOutcome(receipt, response if receipt.status == "succeeded" else None)
