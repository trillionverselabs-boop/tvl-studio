"""example-plugin — register(ctx) wiring.

Three surfaces, one package:
  * agent tools            -> tools.py (ctx.llm exists only inside register)
  * desktop UI             -> desktop/plugin.js (the desktop loader scans this folder)
  * backend routes         -> dashboard/plugin_api.py (/api/plugins/example-plugin/)

Rename checklist: this file, plugin.yaml `name`, dashboard/manifest.json, the
desktop contribution ids, and the tool prefix. The folder name must equal the
plugin id for the desktop half.
"""

from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

# Hermes loads this file as a package (`__init__.py` at the plugin root); pytest
# may import it as a top-level module, where the relative imports below would die
# with "attempted relative import with no known parent package". Registering the
# directory under a real package name keeps both loaders working.
if __package__ in (None, ""):
    __package__ = "example_plugin"
    _self = _sys.modules.setdefault(__package__, _sys.modules[__name__])
    _self.__path__ = [str(_Path(__file__).resolve().parent)]

from .tools import register_tools


def register(ctx) -> None:
    """The only entrypoint Hermes calls. Keep it thin and unbreakable."""
    register_tools(ctx)
