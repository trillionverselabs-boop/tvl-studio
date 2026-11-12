"""Agent tools. Thin handlers: validate, call, return JSON.

Two rules this template already follows, because the catalog review checks them:

1. **A model-controlled value never reaches a path unvalidated.** `run_id` here
   must match the format the plugin mints; `out_dir` must resolve inside
   `data_root()`. Path traversal is the most common blocking finding.
2. **A refusal is data, not an exception.** A handler returns
   `{"error": "..."}` — raising into the host shows the user a stack trace.
"""

from __future__ import annotations

import json
import re
import uuid

from .paths import data_root

RUN_ID_RE = re.compile(r"^[0-9a-f]{12}$")


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def validate_run_id(run_id: str) -> str:
    if not isinstance(run_id, str) or not RUN_ID_RE.match(run_id):
        raise ValueError(f"invalid run_id: {run_id!r}")
    return run_id


def resolve_out_dir(out_dir: str):
    """Resolve a caller-supplied directory and refuse anything outside the data dir."""
    root = data_root().resolve()
    p = root / out_dir if not out_dir.startswith("/") else data_root().__class__(out_dir)
    p = p.resolve()
    if p != root and root not in p.parents:
        raise ValueError(f"out_dir must stay inside {root}: {out_dir!r}")
    p.mkdir(parents=True, exist_ok=True)
    return p


def register_tools(ctx) -> None:
    echo_schema = {
        "name": "example_echo",
        "description": "Echo a string back. Replace this with the real tool.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "What to echo back."},
                "run_id": {"type": "string", "description": "Optional 12-hex run id to echo."},
            },
            "required": ["text"],
        },
    }

    def handle_echo(params, **kwargs):
        text = str(params.get("text", ""))
        run_id = params.get("run_id")
        if run_id:
            try:
                run_id = validate_run_id(str(run_id))
            except ValueError as exc:
                return json.dumps({"error": str(exc), "run_id": str(run_id)})
        return json.dumps({"echo": text, "run_id": run_id})

    ctx.register_tool(name="example_echo", toolset="example", schema=echo_schema,
                      handler=handle_echo)
