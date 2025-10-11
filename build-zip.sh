#!/bin/bash
# Create a zip file containing the build output and essential files
# Usage: Run inside the project directory

set -e

npm run build

VERSION=$(jq -r .version package.json)

ZIPNAME="wuwa-team-randomizer-v${VERSION}.zip"

zip -r "$ZIPNAME" dist CHANGELOG.md LICENSE package.json README.md

mv "$ZIPNAME" ..

echo "Created $ZIPNAME"
