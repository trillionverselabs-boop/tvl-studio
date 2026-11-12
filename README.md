# example-plugin — the template

A Hermes plugin scaffold that is already shaped the way the catalog review wants it.
Copy it, rename it, replace the example tool.

```
cp -r ~/work/plugin-template ~/work/<your-plugin>
```

## Rename (five places, all of them)

| What | Where |
|---|---|
| `name:` | `plugin.yaml` |
| package name in the shim | `__init__.py` (`__package__`), `tests/conftest.py`, `scripts/test.sh` |
| `{"name": ...}` | `dashboard/manifest.json` |
| `id:` and the ids in `register` | `desktop/plugin.js` |
| tool prefix | `tools.py` (`provides_tools` in the manifest must match `register_tool` names) |

The **folder name must equal the plugin id** — the desktop loader scans for it.

## What is already done for you

- `register(ctx)` that runs in isolation (`hermes plugins validate` probes it)
- `paths.py` using `hermes_constants.get_hermes_home()` — the profile-correct home
- one tool whose handler returns JSON errors instead of raising
- `run_id` / `out_dir` guards, with the tests that prove them
- a dashboard namespace loaded **by spec** (never `sys.path`)
- a desktop page that is its own scroll container, built only from the SDK
- `scripts/test.sh` that works from a hyphenated checkout and honours `PYTHON=`
- `docs/DISCLOSURE.md`, `docs/MODEL-CONTROLLED-INPUTS.md` and `CHECKLIST.md`

## Verify before building on it

```bash
cd ~/work/<your-plugin>
hermes plugins validate . --install-deps      # -> Validation passed.
PYTHON=<a venv with pytest> ./scripts/test.sh -q
```

## See also

- `~/work/strategic-arena/docs/MARKETPLACE.md` — the whole submission loop, from
  first PR to re-pin, including the permission trap that costs an hour.
- `CHECKLIST.md` in this folder — the pre-flight, in order.
