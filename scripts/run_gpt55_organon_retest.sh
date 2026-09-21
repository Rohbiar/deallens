#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
: "${OPENAI_API_KEY:?Configure OPENAI_API_KEY in this terminal first}"
.venv/bin/python -u -m deallens.cli run \
  --documents organon \
  --model gpt-5.5-2026-04-23 \
  --model-fields remedy_limitations \
  --max-model-calls 2
