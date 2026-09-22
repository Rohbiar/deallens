# DealLens

DealLens is a runnable Python/SQLite prototype for evidence-linked transaction research and preliminary financing and hedging analysis. One application processes the Bio-Techne, Organon and Uber / Delivery Hero public-source PDFs.

The current deterministic run is `20260922T024418Z-d989f939` at code commit `defe4a3`. It combines scalar extraction, full numbered provisions, a bounded recursive dependency graph, candidate structured interpretations, comparison and timeline views, grounded QA, scenario analytics and an immutable audit trail. Complex structured terms remain unreviewed candidates; they are not legal conclusions or human-verified facts.

## Run locally

Python 3.11 or later:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
python -m deallens.cli serve
```

Open `http://127.0.0.1:8765`. On Windows, activate with `.venv\Scripts\activate`. Original PDFs and precomputed outputs are included, so ordinary review requires no network or API key.

```bash
python -m deallens.cli ask bio_techne "What is the consideration per share?"
python -m deallens.cli ask organon "How may the outside date be extended?"
python -m deallens.cli ask uber_delivery_hero "What financing arrangements are disclosed?"
python -m deallens.cli refresh
```

`refresh` reingests unchanged source bytes using current offline rules and creates a new immutable run. `run` starts a deterministic baseline. `--strict` on `ask` requires human-verified evidence; the supplied run has none and deliberately abstains. Put `--root /path/to/project` before a subcommand when running elsewhere.

## Output meaning

- `supported` is a deterministic normalized scalar or an explicitly reviewed value. Rule confidence is heuristic, not calibrated probability.
- `source_excerpt` preserves full numbered provisions and dependency context while keeping the normalized value null.
- Structured terms separate actors, modalities, triggers, conditions, exceptions, timing, scope, amounts and source IDs. The current 14 terms and 34 statements are all `candidate` and `unreviewed`.
- `requires_review`, `not_found`, `low_confidence` and `conflict` do not produce a canonical answer. Absence is not zero or “not applicable.”

Each run contains document metadata, extraction records, structured terms, comparisons, timelines, risk maps, analytics, QA, exceptions, metrics and scenario CSVs. Structured candidates are stored in JSON and SQLite. The browser exposes their components and uncertainty without asserting that an election occurred or a condition was satisfied. Source changes block answers and PDF viewing against stale runs.

## Evidence and interpretation controls

All three PDFs have pinned hashes and page counts. Organon and Uber filing dates were checked against SEC indexes. Bio-Techne's filing date remains explicitly PDF-metadata-reported.

Numbered sections are expanded through a bounded same-instrument dependency graph with stable section/source IDs, cycle detection and explicit missing, ambiguous, unrecognized or budget-limited dependencies. Displayed QA context and optional model requests use the same graph. Exact citations establish provenance, not semantic correctness.

Candidate structured terms never approve themselves. Material or unknown unresolved dependencies block machine support and analytics use. Strict QA accepts only human-verified evidence. Omitted schedules, incorporated documents, redacted amounts and ambiguous award outcomes remain unresolved.

## Financial conventions

The assignment's synthetic USD 4bn issue and USD 65,000 DV01 per USD 100mm imply USD 2.6mm/bp portfolio DV01. A +25bp benchmark move increases first-order financing-cost PV by USD 65mm and annual coupon cost by USD 10mm; those measures are not added.

Debt is assumed priced at benchmark plus issuer spread. A payer swap offsets benchmark exposure under the simplified model while leaving credit and basis risk. Options and the synthetic deal-contingent swap retain different failure payoffs. The required neutral `failure` scenario assumes no rate move; separate failure-up and failure-down scenarios remain sensitivities. Transaction fees are not automatically offset against hedge losses.

Uber's six-level bridge pricing grid is source-backed and separated from assumed draw and EURIBOR. Public step-up, duration-fee and funding-fee amounts are redacted and remain unavailable.

## Validate and package

```bash
python -m unittest discover -s tests -v
python tests/evaluate_sources.py
PYTHONPATH=. python tests/evaluate_provisions.py
PYTHONPATH=. python tests/build_semantic_predictions.py outputs/$(python -c 'import json; print(json.load(open("outputs/latest.json"))["run_id"])') --output docs/SEMANTIC_PREDICTIONS.json
PYTHONPATH=. python tests/evaluate_semantics.py docs/SEMANTIC_PREDICTIONS.json --output docs/SEMANTIC_EVALUATION.json --no-fail
PYTHONPATH=. python tests/evaluate_requirements.py
PYTHONPATH=. python tests/check_runtime.py
python docs/build_status.py
python docs/package_deliverables.py
```

The integrated suite has 179 tests. The selected evaluations pass 25/25 scalar/source fixtures and 18/18 provision fixtures. The frozen agent-curated semantic set has 72 supported assertions plus four deliberately unresolved cases. Because every structured term remains a candidate, the adapter asserted none: precision is null, recall is 0, all 72 supported assertions are unresolved, and all four source-unresolved cases are respected. This measures conservative behavior over a bounded set, not contract-wide accuracy.

The archive includes code, sources, the current run, lineage, SQLite history, the memo and genuine Git history. Its manifest hashes every included file and excludes credentials and virtual environments. It must be rebuilt and smoke-tested after the final memo.

## Optional model extraction and ownership

Optional bounded model proposals require a privately configured API key. No provider call was made for the current deterministic run. Historical model proposals and the persistent budget ledger are preserved; model output remains unverified even when schema and citations pass. See [MODEL_AND_REVIEW.md](docs/MODEL_AND_REVIEW.md).

[EXECUTION_PLAN.md](EXECUTION_PLAN.md) and [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md) record the actual agent work, corrections and controls. [SUBMISSION_STATUS.md](docs/SUBMISSION_STATUS.md) contains current measured coverage, [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) lists remaining limitations, and [DEMO_GUIDE.md](docs/DEMO_GUIDE.md) provides a short walkthrough. Rohit remains responsible for understanding and accepting the submission; no human legal verification is claimed.
