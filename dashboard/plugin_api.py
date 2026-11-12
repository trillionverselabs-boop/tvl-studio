"""Backend namespace /api/plugins/example-plugin/ — mounted by the dashboard loader.

The loader imports this file standalone (not as part of the agent package), so the
package is brought in by spec with a name derived from the install path. Never put
the plugin directory on sys.path: a plugin that ships `tools.py` then shadows
Hermes's own `tools` package and every host import of it dies.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_PKG_NAME = "_example_plugin_dashboard_" + hashlib.sha256(
    str(_PLUGIN_ROOT).encode("utf-8")).hexdigest()[:16]


def _load_package():
    mod = sys.modules.get(_PKG_NAME)
    if mod is not None:
        return mod
    spec = importlib.util.spec_from_file_location(
        _PKG_NAME, _PLUGIN_ROOT / "__init__.py",
        submodule_search_locations=[str(_PLUGIN_ROOT)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_PKG_NAME] = mod
    spec.loader.exec_module(mod)
    return mod


_load_package()
_paths = importlib.import_module(f".paths", _PKG_NAME)

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    """A route that proves the namespace is mounted, without touching a model."""
    return {"ok": True, "data_root": str(_paths.data_root())}


@router.get("/item/{run_id}")
async def item(run_id: str) -> dict:
    """Any id that becomes a path is validated at the door and answered 400."""
    try:
        from importlib import import_module

        tools = import_module(f".tools", _PKG_NAME)
        run_id = tools.validate_run_id(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"run_id": run_id}
