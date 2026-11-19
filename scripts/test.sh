#!/usr/bin/env bash
# Run the suite whatever the checkout folder is called.
#
# The repo is `tvl-studio` and the package is `tvl_studio`, so pytest's
# root import fails from the checkout directory. Run through a shim dir holding
# the package under a valid name. It honours PYTHON= (the default python3 often
# has no pytest).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/tmp}/plugin-tests.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/tvl_studio"
cp -al "$root"/. "$tmp/tvl_studio/"

cd "$tmp/tvl_studio"
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" -m pytest "$@"
