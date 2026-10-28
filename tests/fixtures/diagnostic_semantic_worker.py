"""Exercise the actual worker with a failing synthetic provider, without inference."""

import sys

from ai_harness_compiler.adapters import codex_cli, semantic_worker_v4


class SyntheticProvider:
    def __init__(self, settings):
        pass

    def generate_json(self, prompt, schema):
        raise ValueError(sys.argv[1])


codex_cli.CodexCompactModel = SyntheticProvider
raise SystemExit(semantic_worker_v4.main())
