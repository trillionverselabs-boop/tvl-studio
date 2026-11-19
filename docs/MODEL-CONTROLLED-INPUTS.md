# Model-controlled inputs — what happens if each one is hostile?

| Input | Where it comes in | What it can touch | If it is hostile | Proven by |
|---|---|---|---|---|
| `name` | `studio_import_script`, `/import` | project id slug | slugified `[^a-z0-9]+→-`, capped 48 chars + random suffix; never a raw path | `tests/test_state.py` |
| `script` | `studio_import_script`, `/import` | storyboard JSON, captions | parsed as data; HTML-escaped into compositions; empty → typed error | `tests/test_parser.py`, `tests/test_assemble.py` |
| `project` | every tool/route | filesystem paths | `^[a-z0-9][a-z0-9-]{0,63}$` + parent-dir check before any join; `../` refused with JSON error / HTTP 400 | `tests/test_tools.py`, `tests/test_state.py` |
| `shot_id` | attach/voiceover | filesystem paths | `^s\d{2,3}$` + must exist in the project | `tests/test_state.py` |
| `character` | `studio_attach_portrait` | filesystem paths | must exist in cast; filename sanitized `[^A-Z0-9]+→_` | `tests/test_state.py` |
| `image_path` | attach tools | filesystem read+copy | must be an existing file with an image extension; copied into the project (source read-only) | `tests/test_tools.py` |
| `brand` / `kit.id` | import, apply, save | filesystem paths | `^[a-z0-9][a-z0-9-]{0,63}$`; unknown kit names the alternatives | `tests/test_brands.py` |
| `kit` object | `studio_brands save` | kit JSON | normalized: voices filtered to the known pool, speed clamped 0.7–1.5, music mode enum, volume clamped | `tests/test_brands.py` |
| `kit.music.file` | assembly | filesystem read | must resolve inside the data dir or bundled data; outside → refused | `tests/test_assemble.py` |
| `style` | import | image prompts only | plain text appended to prompts; never a path or command | `tests/test_state.py` |

No tool parameter becomes a shell string: every subprocess uses list arguments,
no `shell=True`. No URL is fetched by the plugin.
