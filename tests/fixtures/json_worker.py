"""Trusted offline subprocess fixture; never invokes a model or reads project assets."""

import json
import subprocess
import sys
import time
from pathlib import Path

raw = sys.stdin.buffer.read()
mode = sys.argv[1]
if mode == "timeout":
    time.sleep(30)
elif mode == "overflow":
    sys.stdout.buffer.write(b"x" * (1024 * 1024))
elif mode == "invalid":
    sys.stdout.write("not JSON")
elif mode == "exit":
    raise SystemExit(7)
elif mode == "child":
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    Path(sys.argv[2]).write_text(str(child.pid))
    time.sleep(30)
elif mode == "flow":
    payload = json.loads(raw)
    title = payload["response_schema"]["title"]
    file = sys.argv[2] if title == "AnalysisProposalV4" else sys.argv[3]
    response = Path(file).read_text(encoding="utf-8")
    sys.stdout.write(json.dumps({"response": response}))
else:
    sys.stdout.write(json.dumps({"response": json.dumps({"received": json.loads(raw)})}))
