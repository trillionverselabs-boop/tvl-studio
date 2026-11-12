# Disclosure (catalog rule 13)

Rule 13: what a user would want to know before installing goes in the **PR
description** and the plugin's **README**. Undisclosed behaviour found in review is
a request for changes.

Fill every line below before submitting. "None" is an answer; blank is not.

- **Network calls:** *(which endpoints, when, with what credentials — e.g. "the
  inference endpoint for the active model via `ctx.llm`; nothing else")*
- **Reads outside the plugin's data dir:** *(package files? the app's own files?
  none?)*
- **Shell commands:** *(none)*
- **Background processes:** *(none — no daemon, no auto-update, no telemetry)*
- **Stored credentials:** *(none — no `.env`, no `auth.json`, no vendor token
  files; model access goes through `ctx.llm`)*
- **Model requirements:** *(which model runs, what a free tier costs, what to do
  when it fails — and where the wait actually lands)*

Keep the same wording in four places, and pin it with a test: the UI control, the
README, the docs page, and the entry's `known_issues`.
