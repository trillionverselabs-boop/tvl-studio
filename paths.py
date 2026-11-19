"""Where this plugin is allowed to write.

Use the host's own resolution: `hermes_constants.get_hermes_home()` follows the
active profile (context override -> $HERMES_HOME -> platform default). Reading
`os.environ["HERMES_HOME"]` alone misses the override and writes into the wrong
profile under multiplexing — that was a review finding once.
"""

from __future__ import annotations

import os
from pathlib import Path

PLUGIN_ID = "tvl-studio"


def _hermes_home() -> Path:
    try:
        from hermes_constants import get_hermes_home

        return Path(get_hermes_home())
    except Exception:
        return Path(os.environ.get("HERMES_HOME") or (Path.home() / ".hermes"))


def data_root() -> Path:
    """`<hermes home>/plugin-data/<id>`, with a plain fallback outside Hermes."""
    home = _hermes_home()
    try:
        from plugins.plugin_storage import plugin_data_dir  # type: ignore

        p = Path(plugin_data_dir(PLUGIN_ID))
        if str(p).startswith(str(home)):        # never escape the active home
            return p
    except Exception:
        pass
    return home / PLUGIN_ID
