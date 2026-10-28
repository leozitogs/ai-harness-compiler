"""Fixed exit categories, bound to receipts; never retain provider exception text."""

from typing import Literal, Self

from pydantic import model_validator

from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.supervised_transport import TransportReceiptV1

WorkerStage = Literal["input", "setup", "provider", "output", "unknown"]
WorkerCategory = Literal[
    "request-limit",
    "request-invalid",
    "provider-unavailable",
    "subscription-required",
    "authentication-timeout",
    "provider-timeout",
    "provider-error",
    "provider-output-limit",
    "provider-protocol",
    "provider-tool-event",
    "provider-incomplete",
    "provider-failed",
    "output-encoding",
    "output-io",
    "worker-internal",
    "provider-input-limit",
    "provider-io",
    "provider-setup",
    "input-io",
    "unknown",
    "not-worker-failure",
]

# Values fit POSIX's eight-bit exit status as well as Windows. Code 2 stays unknown.
EXIT_CATEGORIES: dict[int, tuple[WorkerStage, WorkerCategory]] = {
    20: ("input", "request-limit"),
    21: ("input", "request-invalid"),
    22: ("provider", "provider-unavailable"),
    23: ("provider", "subscription-required"),
    24: ("provider", "authentication-timeout"),
    25: ("provider", "provider-timeout"),
    26: ("provider", "provider-error"),
    27: ("provider", "provider-output-limit"),
    28: ("provider", "provider-protocol"),
    29: ("provider", "provider-tool-event"),
    30: ("provider", "provider-incomplete"),
    31: ("provider", "provider-failed"),
    32: ("output", "output-encoding"),
    33: ("output", "output-io"),
    34: ("unknown", "worker-internal"),
    35: ("provider", "provider-input-limit"),
    36: ("provider", "provider-io"),
    37: ("setup", "provider-setup"),
    38: ("input", "input-io"),
}


def receipt_category(receipt: TransportReceiptV1) -> tuple[WorkerStage, WorkerCategory]:
    if receipt.status != "failed" or receipt.failure_code != "worker-failed":
        return "unknown", "not-worker-failure"
    if not receipt.root_reaped:
        return "unknown", "unknown"
    return EXIT_CATEGORIES.get(receipt.exit_code or 0, ("unknown", "unknown"))


class WorkerDiagnosticV1(Contract):
    schema_version: Literal["WorkerDiagnostic/v1"] = "WorkerDiagnostic/v1"
    receipt: TransportReceiptV1
    stage: WorkerStage
    category: WorkerCategory
    attribution: Literal["worker-reported-category-not-root-cause"] = (
        "worker-reported-category-not-root-cause"
    )

    @model_validator(mode="after")
    def exact_category(self) -> Self:
        if (self.stage, self.category) != receipt_category(self.receipt):
            raise ValueError("Diagnostic must preserve the observed receipt category")
        return self


def diagnose_worker(receipt: TransportReceiptV1) -> WorkerDiagnosticV1:
    receipt = TransportReceiptV1.model_validate(receipt.model_dump())
    stage, category = receipt_category(receipt)
    return WorkerDiagnosticV1(receipt=receipt, stage=stage, category=category)
