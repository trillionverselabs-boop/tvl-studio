"""tvl-studio — register(ctx) wiring.

Three surfaces, one package:
  * agent tools            -> tools.py (the repeatable storyboard pipeline)
  * desktop UI             -> desktop/plugin.js (the TVL-branded studio board)
  * backend routes         -> dashboard/plugin_api.py (/api/plugins/tvl-studio/)

The folder name must equal the plugin id for the desktop half.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

# Hermes loads this file as a package (`__init__.py` at the plugin root); pytest
# may import it as a top-level module, where the relative imports below would die
# with "attempted relative import with no known parent package". Registering the
# directory under a real package name keeps both loaders working.
if __package__ in (None, ""):
    __package__ = "tvl_studio"
    _self = _sys.modules.setdefault(__package__, _sys.modules[__name__])
    _self.__path__ = [str(_Path(__file__).resolve().parent)]

from .tools import register_tools


def register(ctx) -> None:
    """The only entrypoint Hermes calls. Keep it thin and unbreakable."""
    register_tools(ctx)
    skill = _Path(__file__).resolve().parent / "skills" / "tvl-studio"
    if skill.is_dir():
        try:
            ctx.register_skill("tvl-studio", str(skill))
        except Exception:
            pass  # older hosts without register_skill still get the tools
