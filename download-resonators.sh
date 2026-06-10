#!/usr/bin/env bash

# ─────────────────IMPORTANT!!!────────────────
# This script was generated using an LLM, please read it over before using!!!

# ─────────────────────────────────────────────────────────────
# download_resonators.sh
# Downloads Resonator images from the Wuthering Waves fandom wiki
# via the MediaWiki API (no scraping, no 403s) and converts them
# to 128×128 lossless WebP via ImageMagick.
#
# Usage:
#   ./download_resonators.sh "Lumi" "Rover" "Bob Lastname"
#
# Output: ./resonators/<Name>.webp  (128×128, lossless)
# ─────────────────────────────────────────────────────────────

set -euo pipefail

API_URL="https://wutheringwaves.fandom.com/api.php"
CDN_HOST="static.wikia.nocookie.net"
OUT_DIR="./resonators"

# ── Dependency checks ─────────────────────────────────────────
for cmd in curl python3 convert; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "ERROR: '$cmd' is required but not installed." >&2
    exit 1
  fi
done

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 \"Name\" \"First Last\" ..."
  echo "Example: $0 \"Lumi\" \"Rover\" \"Bob Lastname\""
  exit 1
fi

mkdir -p "$OUT_DIR"

for name in "$@"; do
  wiki_name="${name// /_}"
  file_title="File:Resonator_${wiki_name}.png"
  out_file="${OUT_DIR}/${wiki_name}.webp"

  echo "──────────────────────────────────────"
  echo "Processing : $name"
  echo "File title : $file_title"

  # ── Step 1: Query MediaWiki API for the direct CDN URL ──────
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

  # Extract the URL from the JSON response using python3
  img_url=$(echo "$api_response" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    pages = d['query']['pages']
    page = list(pages.values())[0]
    if 'imageinfo' not in page:
        print('NOT_FOUND')
    else:
        print(page['imageinfo'][0]['url'])
except Exception as e:
    print('ERROR:' + str(e))
" 2>&1)

  if [[ "$img_url" == "NOT_FOUND" ]]; then
    echo "ERROR: '$file_title' not found on the wiki. Check the name spelling." >&2
    continue
  fi

  if [[ "$img_url" == ERROR:* ]]; then
    echo "ERROR: Failed to parse API response for '$name': $img_url" >&2
    continue
  fi

  echo "Image URL  : $img_url"

  # ── Step 2: Download the image from the CDN ─────────────────
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
    echo "ERROR: HTTP $http_code when downloading image for '$name'. Skipping." >&2
    rm -f "$tmp_file"
    continue
  fi

  mime=$(file --brief --mime-type "$tmp_file")
  if [[ "$mime" != image/* ]]; then
    echo "ERROR: Expected an image but got '$mime' for '$name'. Skipping." >&2
    rm -f "$tmp_file"
    continue
  fi

  # ── Step 3: Convert to 128×128 WebP ─────────────────────────
  convert "$tmp_file" \
    -filter Lanczos \
    -resize 128x128 \
    -quality 95 \
    "$out_file"

  rm -f "$tmp_file"
  echo "Saved      : $out_file  ✓"
done

echo ""
echo "Done! Files are in: ${OUT_DIR}/"