#!/bin/sh
# Regenerates every derived file (the inner pages from site/wordpress/index.html
# and the generators, and the easy tier's model inputs from the pages), then
# checks the result against SHA256SUMS.
set -eu
cd "$(dirname "$0")/.."
python3 tools/make_wp_pages.py >/dev/null
python3 tools/make_wix_pages.py >/dev/null
mkdir -p inputs/easy
for case in wordpress wix; do
  python3 tools/render_input.py "$case" > "inputs/easy/$case.txt"
done
sha256sum -c --quiet SHA256SUMS && echo "site and input bytes match SHA256SUMS"
