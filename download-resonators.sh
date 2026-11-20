#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"Name\" \"First Last\" ..." >&2
    exit 2
fi

for cmd in python3 convert; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: '$cmd' is required but not installed." >&2
        exit 1
    fi
done

python3 "$SCRIPT_DIR/scripts/import_resonators.py" "$@"
