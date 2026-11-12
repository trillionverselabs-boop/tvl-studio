# Before you submit — pre-flight

Run this **before** the work, not at the end. Every line here has cost someone a
review round.

## 1. Permissions (do this first)

- [ ] `gh auth status` shows a token that can **write to the upstream repo**, not
      just your fork. A fine-grained PAT cannot write to a public repo you are not a
      member of — it 403s on `addComment` and `updatePullRequest`.
- [ ] If it can't: `gh auth login --web`, hand the user the one-time code. Do not
      ask them to store or paste a token.
- [ ] Confirm with a read-only call that the PR number exists and is yours.

## 2. The tree

- [ ] `hermes plugins validate . --install-deps` → `Validation passed.`, `security
      scan — safe` on a **clean clone at the commit you will pin**.
- [ ] The plugin's own suite is green through `./scripts/test.sh -q` with `PYTHON=`
      pointing at an interpreter that has pytest (and pyyaml if the tests parse YAML).
- [ ] `sys.path` never contains the plugin directory; `tools.py` would shadow the
      host's own `tools` package.
- [ ] `version:` in `plugin.yaml` matches the code you are pinning.

## 3. The three review classes

- [ ] Every model-controlled value that becomes a **path** is validated first.
- [ ] Every model-controlled value that becomes a **URL** is resolved and refused
      unless global — on the request and on every redirect.
- [ ] Every model-controlled value that becomes a **write** resolves inside
      `data_root()`.

## 4. Disclosure

- [ ] `docs/DISCLOSURE.md` filled in; the same facts in the README and the PR body.
- [ ] `docs/MODEL-CONTROLLED-INPUTS.md` has a row per input, each with a test.
- [ ] A test pins the user-facing copy, so the next UI rewrite can't silently drop it.

## 5. The desktop half

- [ ] Rendered, not just read: stub the SDK and walk the element tree (a misplaced
      `]}),` parses fine and renders the wrong tree).
- [ ] The page is its own scroll container (`h-full min-h-0 flex-1 overflow-y-auto`).
- [ ] A dialog with a growing form has a resolved height (`h-[78vh]`, not `max-h`),
      with title and footer **outside** the scroller.
- [ ] `BUILD` bumped, and the badge in the window matches `plugin.yaml`.

## 6. The entry

- [ ] `sha:` is the full 40-char commit; `image:`/`screenshots:` point at that sha
      and return `HTTP/2 200`.
- [ ] `version:` in the entry matches the manifest.
- [ ] `known_issues` says what a user needs before installing — no invented prices.
