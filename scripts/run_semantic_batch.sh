#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
# Inherits the key from the invoking terminal. Never saves or prints it.
: "${OPENAI_API_KEY:?Configure OPENAI_API_KEY in this terminal first}"
.venv/bin/python -u -m deallens.cli run \
  --model gpt-4.1-mini-2025-04-14 \
  --model-fields target parent_or_bidder guarantors_or_covered_parties \
    extension_dates_and_conditions fee_triggers_and_tails \
    vested_options unvested_options rsus psus award_cohort_differences \
    regulatory_approvals remedy_limitations funding_sources financing_conditions \
    financing_fees_and_stepups \
  --max-model-calls 45
