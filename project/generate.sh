#!/usr/bin/env bash
# Generate .chn schematics from project/ Python files via Schemify import.
#
# Usage: ./project/generate.sh
# Requires: nix develop (provides schemify + pyspice_rs)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCHEMIFY="${SCHEMIFY:-schemify}"

if ! command -v "$SCHEMIFY" &>/dev/null; then
    echo "error: schemify not found. Run inside 'nix develop' or set SCHEMIFY env var." >&2
    exit 1
fi

cd "$ROOT"

# Clean previous output
rm -rf components/ primitives/ testbenches/ top/

# Import all PySpice files from project/ recursively (auto-detects type from content)
"$SCHEMIFY" --import-project -r project/

# Route top-level schematic to top/ (Config.toml expects top/*.chn)
mkdir -p top
if [ -f components/mvm_top.chn ]; then
    mv components/mvm_top.chn top/
fi

# Summary
echo "Import complete:"
echo "  components:  $(find components -name '*.chn' 2>/dev/null | wc -l) files"
echo "  primitives:  $(find primitives -name '*.chn_prim' 2>/dev/null | wc -l) files"
echo "  testbenches: $(find testbenches -name '*.chn_tb' 2>/dev/null | wc -l) files"
echo "  top:         $(find top -name '*.chn' 2>/dev/null | wc -l) files"
