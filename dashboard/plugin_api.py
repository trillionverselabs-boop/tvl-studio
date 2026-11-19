"""Backend namespace /api/plugins/tvl-studio/ — mounted by the dashboard loader.

Loaded standalone (not as part of the agent package): the package is brought in
by spec with a name derived from the install path. Never put the plugin
directory on sys.path (a plugin shipping tools.py would shadow the host's own
tools package).
"""

from __future__ import annotations

import base64
import hashlib
import importlib
import importlib.util
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
_PKG_NAME = "_tvl_studio_dashboard_" + hashlib.sha256(
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
_paths = importlib.import_module(".paths", _PKG_NAME)
_storyboard = importlib.import_module(".engine.storyboard", _PKG_NAME)
_brands = importlib.import_module(".engine.brands", _PKG_NAME)
_voiceover = importlib.import_module(".engine.voiceover", _PKG_NAME)
_assemble = importlib.import_module(".engine.assemble", _PKG_NAME)

router = APIRouter()


def _thumb(path_str: str | None) -> str | None:
    """Small JPEG data URL for the board; None when there is no image yet."""
    if not path_str:
        return None
    p = Path(path_str)
    if not p.is_file():
        return None
    try:
        import subprocess
        proc = subprocess.Popen(
            [_voiceover.ffmpeg(), "-v", "error", "-i", str(p),
             "-vf", "scale=360:-2", "-frames:v", "1", "-f", "image2pipe",
             "-c:v", "mjpeg", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        out, _ = proc.communicate(timeout=20)
        if proc.returncode == 0 and out:
            return "data:image/jpeg;base64," + base64.b64encode(out).decode()
    except Exception:
        pass
    return None


def _detail(proj: dict) -> dict:
    cast = {}
    for name, c in proj["cast"].items():
        cast[name] = {**c, "thumb": _thumb(c.get("portrait"))}
    shots = [{**s, "thumb": _thumb(s.get("image"))} for s in proj["shots"]]
    return {"project": _storyboard.summary(proj), "cast": cast, "shots": shots,
            "busy": proj.get("busy"), "film": proj.get("film"),
            "film_duration": proj.get("film_duration"),
            "next_action": _storyboard.next_action(proj)}


@router.get("/health")
async def health() -> dict:
    return {"ok": True, "data_root": str(_paths.data_root())}


@router.get("/brands")
async def brands_list() -> dict:
    return {"brands": _brands.list_kits()}


@router.get("/projects")
async def projects() -> dict:
    return {"projects": _storyboard.list_projects()}


@router.get("/project/{project_id}")
async def project_detail(project_id: str) -> dict:
    try:
        return await run_in_threadpool(
            lambda: _detail(_storyboard.load(project_id)))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class ImportBody(BaseModel):
    name: str
    script: str
    brand: str = _brands.DEFAULT_KIT
    style: str = ""


@router.post("/import")
async def import_script(body: ImportBody) -> dict:
    try:
        proj = await run_in_threadpool(
            lambda: _storyboard.create(body.name, body.script, body.brand, body.style))
        return _detail(proj)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class BrandBody(BaseModel):
    brand: str


@router.post("/project/{project_id}/brand")
async def set_brand(project_id: str, body: BrandBody) -> dict:
    try:
        proj = await run_in_threadpool(
            lambda: _storyboard.set_brand(project_id, body.brand))
        return _detail(proj)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


def _guard_busy(project_id: str) -> None:
    proj = _storyboard.load(project_id)
    if proj.get("busy"):
        raise HTTPException(status_code=409,
                            detail=f"project is busy: {proj['busy']}")


@router.post("/project/{project_id}/voiceover")
async def voiceover(project_id: str) -> dict:
    try:
        _guard_busy(project_id)
        return await run_in_threadpool(_voiceover.run, project_id)
    except HTTPException:
        raise
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/project/{project_id}/assemble")
async def assemble(project_id: str) -> dict:
    try:
        _guard_busy(project_id)
        return await run_in_threadpool(_assemble.run, project_id)
    except HTTPException:
        raise
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
