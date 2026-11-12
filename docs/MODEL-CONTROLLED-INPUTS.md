# Model-controlled inputs — what happens if each one is hostile?

Every value the model can pass to a tool or route, what it can touch, what happens
if it is hostile, and the test that proves it. **Run this table before every
submission. A blank cell is a finding.**

| Input | Where it comes in | What it can touch | If it is hostile | Proven by |
|---|---|---|---|---|
| `text` | `example_echo` | the reply | echoed verbatim — bounded and harmless, but anything that becomes a prompt needs the budget sentence | `tests/test_tools.py` |
| `run_id` | `example_echo`, `/item/{run_id}` | filesystem paths | `../` walks out of the data dir; refused by `^[0-9a-f]{12}$` before the join, with a JSON error / HTTP 400 | `tests/test_tools.py` |
| `out_dir` | any writer | filesystem write | a path anywhere the user can write; resolved and refused outside `data_root()` | `tests/test_tools.py` |
| `urls[]` | *(add when a tool fetches)* | outbound HTTP | SSRF: LAN, link-local, cloud metadata, and redirects into the LAN. Resolve the host and refuse anything not global, on the request **and each redirect** | *(add the test with the tool)* |
| model / provider response | any `ctx.llm` call | run length, degraded flag | a 429 or an empty reply; retried and spaced, and never reported as a clean result | *(add the test)* |

## Before a submission

1. Add a row for every new tool parameter and route parameter.
2. Write the test that proves the hostile case is handled — before the parameter ships.
3. If the answer is "nothing, it is unbounded", that is the finding.
