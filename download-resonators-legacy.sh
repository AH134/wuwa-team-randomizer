#!/usr/bin/env bash

# Legacy image-only downloader. New imports should use download-resonators.sh.
# Downloads Resonator images from the Wuthering Waves wiki and converts them
# to 128x128 WebP files in ./resonators.
#
# Usage:
#   ./download-resonators-legacy.sh "Lumi" "Rover" "Bob Lastname"

set -euo pipefail

API_URL="https://wutheringwaves.fandom.com/api.php"
OUT_DIR="./resonators"

for cmd in curl python3 convert file; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "ERROR: '$cmd' is required but not installed." >&2
        exit 1
    fi
done

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 \"Name\" \"First Last\" ..." >&2
    exit 2
fi

mkdir -p "$OUT_DIR"

for name in "$@"; do
    wiki_name="${name// /_}"
    file_title="File:Resonator_${wiki_name}.png"
    out_file="${OUT_DIR}/${wiki_name}.webp"

    echo "Processing: $name"

    api_response=$(curl \
        --silent \
        --show-error \
        --get \
        --user-agent "Mozilla/5.0 (compatible; resonator-downloader/1.0)" \
        --data-urlencode "action=query" \
        --data-urlencode "titles=${file_title}" \
        --data-urlencode "prop=imageinfo" \
        --data-urlencode "iiprop=url" \
        --data-urlencode "format=json" \
        "$API_URL")

    img_url=$(echo "$api_response" | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    page = list(data['query']['pages'].values())[0]
    print(page['imageinfo'][0]['url'] if 'imageinfo' in page else 'NOT_FOUND')
except Exception as error:
    print('ERROR:' + str(error))
" 2>&1)

    if [[ "$img_url" == "NOT_FOUND" ]]; then
        echo "ERROR: '$file_title' not found on the wiki." >&2
        continue
    fi
    if [[ "$img_url" == ERROR:* ]]; then
        echo "ERROR: Failed to parse API response for '$name': $img_url" >&2
        continue
    fi

    tmp_file=$(mktemp /tmp/resonator_XXXXXX)
    http_code=$(curl \
        --silent \
        --show-error \
        --location \
        --max-redirs 5 \
        --user-agent "Mozilla/5.0 (compatible; resonator-downloader/1.0)" \
        --referer "https://wutheringwaves.fandom.com/" \
        --output "$tmp_file" \
        --write-out "%{http_code}" \
        "$img_url")

    if [[ "$http_code" -lt 200 || "$http_code" -ge 400 ]]; then
        echo "ERROR: HTTP $http_code when downloading image for '$name'." >&2
        rm -f "$tmp_file"
        continue
    fi

    mime=$(file --brief --mime-type "$tmp_file")
    if [[ "$mime" != image/* ]]; then
        echo "ERROR: Expected an image but got '$mime' for '$name'." >&2
        rm -f "$tmp_file"
        continue
    fi

    convert "$tmp_file" \
        -filter Lanczos \
        -resize 128x128 \
        -quality 95 \
        "$out_file"

    rm -f "$tmp_file"
    echo "Saved: $out_file"
done

echo "Done! Files are in: ${OUT_DIR}/"
