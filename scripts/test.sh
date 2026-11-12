#!/usr/bin/env bash
# Run the suite whatever the checkout folder is called.
#
# The repo is `example-plugin` and the package is `example_plugin`, so pytest's
# root import fails from the checkout directory. Run through a shim dir holding
# the package under a valid name. It honours PYTHON= (the default python3 often
# has no pytest).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/plugin-tests.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/example_plugin"
cp -al "$root"/. "$tmp/example_plugin/"

cd "$tmp/example_plugin"
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" -m pytest "$@"
