#!/bin/sh
# regenerate data/questions.json from the parsed IDML + all editorial patches
set -e
cd "$(dirname "$0")/.."
python3 data/import/convert_surg.py
python3 tools/review2patch.py
python3 data/import/b39_surg_src.py
for f in data/import/[5-9]*_src.py; do [ -f "$f" ] && python3 "$f"; done
rm -f data/patches/applied.txt data/corrections.csv data/patches/600-topics.json
python3 tools/apply.py
python3 tools/autotopics.py
python3 tools/apply.py
