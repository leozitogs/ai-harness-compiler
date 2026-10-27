"""Run the actual JSON worker with a synthetic provider and selected pipe encoding."""

import json
import sys

from ai_harness_compiler.adapters import codex_cli, semantic_worker_v4

sys.stdout.reconfigure(encoding=sys.argv[1])


class SyntheticProvider:
    def __init__(self, settings):
        pass

    def generate_json(self, prompt, schema):
        assert prompt == "Offline Unicode transport test"
        return json.dumps({"text": sys.argv[2]}, ensure_ascii=False)


codex_cli.CodexCompactModel = SyntheticProvider
raise SystemExit(semantic_worker_v4.main())
