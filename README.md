# DealLens

DealLens is a runnable Python/SQLite prototype for evidence-linked transaction research and preliminary financing and hedging analysis. One application processes the Bio-Techne, Organon and Uber / Delivery Hero source PDFs.

The current implementation includes scalar extraction, full numbered source sections with cross-reference context, a read-only browser and CLI, scenario analysis, and an immutable audit trail. **Complex source excerpts are not complete legal interpretations.** See [current submission status](docs/SUBMISSION_STATUS.md) for measured coverage and remaining limitations.

## Run locally

Python 3.11 or later:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
python -m deallens.cli serve
```

Open http://127.0.0.1:8765. On Windows, activate with `.venv\Scripts\activate`. Original PDFs and precomputed results are included in the review archive, so serving requires no network or API key.

```bash
python -m deallens.cli ask bio_techne "What is the consideration per share?"
python -m deallens.cli ask organon "How may the outside date be extended?"
python -m deallens.cli ask uber_delivery_hero "What financing arrangements are disclosed?"
python -m deallens.cli refresh
```

`refresh` reingests the unchanged source bytes with current metadata and extraction rules, preserves historical model proposals, and creates a new run without provider calls. `run` starts a new deterministic baseline. `--strict` on `ask` requires human-verified values; the supplied run has none and deliberately abstains. Put `--root /path/to/project` before the subcommand when running elsewhere.

## What the outputs mean

- `supported`: a deterministic normalized value, or an explicitly reviewed value. Machine support is not human verification. Rule confidence is heuristic, not calibrated probability.
- `source_excerpt`: complete numbered sections with exact page spans and available reference/definition context. Normalized values remain null and QA stays partial. Nested references, omitted schedules and interpretation can remain unresolved.
- `requires_review`, `not_found`, `low_confidence`, `conflict`: no supported normalized answer. Conflicts block canonical values; absence is not a zero fee or “not applicable.”

Each immutable run contains document metadata, extraction records, comparisons, timeline, risk map, analytics, QA, exceptions, metrics and scenario CSVs. SQLite preserves history. The browser shows original PDFs, evidence, comparisons, contractual clocks, risk implications, analytics and QA. Source changes block answers and PDF viewing against stale runs.

## Source and extraction controls

All three stored PDFs match fresh publisher downloads and have pinned hashes and page counts. Organon and Uber filing dates were checked against SEC filing indexes. Bio-Techne's date is explicitly PDF-metadata-reported; its filing index was inaccessible. Matching a publisher PDF does not establish that omitted schedules or incorporated documents are available.

A shared 42-field catalog drives the same rules across all cases. Section-aware extraction preserves continuation pages, locates same-instrument section references and selected defined terms, and labels missing or bounded context. It does not collapse different legal language into a claimed equivalence. Human review uses versioned CLI decisions; local reviewer identity is self-attested. Agent annotations never grant human approval.

## Financial conventions

The assignment's USD 4bn issue and USD 65,000 DV01 per USD 100mm imply USD 2.6mm/bp portfolio DV01. A +25bp benchmark move increases first-order financing cost PV by USD 65mm and annual coupon cost by USD 10mm. Those measures are never added together.

Debt is assumed priced at benchmark plus issuer spread: 4.25% + 1.00% = 5.25%. The 4.40% swap rate implies a 15bp initial swap spread; adding it again to the debt coupon would double-count exposure. A payer swap follows benchmark plus swap-spread movements, leaving issuer credit spread unhedged. Equal benchmark and credit DV01 is an explicit assumption.

Four strategies cover unhedged debt, a forward-starting payer swap, a payer option and a synthetic deal-contingent payer swap. Premiums, contingent fees and roll costs are assumptions. Option results are expiry payoffs, not market valuations. Positive net incremental cost is worse for the issuer. Deal termination fees are not automatically offset against hedge losses.

Validation cases use explicitly synthetic USD/EUR financing slices. Uber also has a source-backed six-level bridge pricing grid, separated from assumed draw and EURIBOR. Public step-up amounts, funding fees and duration fees are redacted; illustrative values are never represented as extracted terms. The bridge sensitivity is separate from the seven-year refinancing DV01.

## Validate and package

```bash
python -m unittest discover -s tests -v
python tests/evaluate_sources.py
PYTHONPATH=. python tests/evaluate_provisions.py
PYTHONPATH=. python tests/evaluate_requirements.py
PYTHONPATH=. python tests/check_runtime.py
python docs/build_status.py
python docs/package_deliverables.py
```

The runtime check opens a temporary loopback HTTP server. Tests cover selected source fixtures and engineering controls; they do not measure contract-wide semantic precision or recall. See [PROVISION_EVALUATION.json](docs/PROVISION_EVALUATION.json), [SOURCE_EVALUATION.json](docs/SOURCE_EVALUATION.json) and [TEST_RESULTS.txt](docs/TEST_RESULTS.txt).

The archive contains code, sources, the current run, selected ancestor runs, SQLite history, a review packet, the three-page memo and genuine Git history. Its manifest hashes every included file. Credentials and virtual environments are excluded. This is a review/submission candidate with disclosed limitations, not an assertion of complete semantic coverage.

## Optional model extraction

`run --model YOUR_MODEL_ID` supports bounded schema-constrained proposals with audited requests and exact citations. An API key must be configured privately. No new paid run was made during the section-aware continuation. The existing local budget ledger is preserved; see [MODEL_AND_REVIEW.md](docs/MODEL_AND_REVIEW.md) for historical evaluations and the review protocol. Model proposals cannot approve themselves.

## Ownership and scope

[EXECUTION_PLAN.md](EXECUTION_PLAN.md) and [AGENT_WORKFLOW.md](AGENT_WORKFLOW.md) document actual agent work, retained changes and corrections. [KNOWN_ISSUES.md](docs/KNOWN_ISSUES.md) distinguishes assignment gaps from production work. Review the calculations, sources, code and limitations before submitting; no human verification or time savings are invented. For a walkthrough use [DEMO_GUIDE.md](docs/DEMO_GUIDE.md).
