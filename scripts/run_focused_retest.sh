#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
: "${OPENAI_API_KEY:?Configure OPENAI_API_KEY in this terminal first}"
.venv/bin/python -u -m deallens.cli run \
  --model gpt-4.1-mini-2025-04-14 \
  --model-fields vested_options fee_triggers_and_tails remedy_limitations financing_conditions \
  --max-model-calls 12
