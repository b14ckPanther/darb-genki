#!/bin/sh
# Renders all four Genki directions at full size into ../  (blender on PATH)
cd "$(dirname "$0")"
for d in gather mesh trace kintsugi; do blender -b -P genki.py -- "$d" "$PWD/../$d-full.png" "${SIZE:-1024}" "${SAMPLES:-192}" 2>&1 | grep -E "rendered|Error|Traceback"; done
