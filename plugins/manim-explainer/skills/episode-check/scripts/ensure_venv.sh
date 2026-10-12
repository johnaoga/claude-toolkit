#!/usr/bin/env bash
# Create (once) and print the path of the Python used for headless checks.
# Usage: PY=$(bash ensure_venv.sh)
set -euo pipefail

VENV="${MANIM_EXPLAINER_VENV:-$HOME/.cache/manim-explainer/venv}"

if [ ! -x "$VENV/bin/python" ]; then
  # manim has no wheels for the newest Pythons; prefer 3.12, then 3.11.
  BASE=""
  for v in 3.12 3.11; do
    if command -v pyenv >/dev/null 2>&1; then
      cand=$(ls -d "$(pyenv root)"/versions/$v.*/bin/python 2>/dev/null | sort -V | tail -1 || true)
      if [ -n "$cand" ]; then BASE="$cand"; break; fi
    fi
    if command -v "python$v" >/dev/null 2>&1; then BASE="$(command -v "python$v")"; break; fi
  done
  if [ -z "$BASE" ]; then
    echo "No Python 3.12/3.11 found (pyenv or PATH). Install one, e.g. 'pyenv install 3.12'." >&2
    exit 1
  fi
  mkdir -p "$(dirname "$VENV")"
  "$BASE" -m venv "$VENV" >&2
  "$VENV/bin/python" -m pip install -q --upgrade pip >&2
  "$VENV/bin/python" -m pip install -q manim manim-voiceover numpy pillow >&2
fi

for tool in ffmpeg latex dvisvgm; do
  command -v "$tool" >/dev/null 2>&1 || echo "warning: '$tool' not on PATH (needed by Manim; latex/dvisvgm only for MathTex)" >&2
done

echo "$VENV/bin/python"
