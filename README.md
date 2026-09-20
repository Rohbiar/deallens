# DealLens

DealLens is a runnable public-source research prototype for the Mizuho Derivatives Analytics & AI Solutions Engineer case. It connects original PDF pages to structured evidence, comparisons, timelines, a local question interface and reproducible financing sensitivities.

**This is an initial implementation for review, not a submission-ready claim of complete legal extraction.** The deterministic baseline supports a limited group of amounts, dates and explicit conditions. Complex provisions are retrieved as candidate evidence with null normalized values. They require an actual semantic extraction/review pass. The UI makes this distinction visible. No human verification or live-model extraction is claimed.

## Continuation verification (2026-09-20)

54 unit/control tests and 16 selected source fixtures pass. The bounded retriever reaches all 16 fixture excerpts after an ISO-currency retrieval fix. These are agent-curated checks, not complete semantic accuracy or human review. Browser checks confirmed the supported Bio-Techne answer, strict-mode abstention and Uber price-qualifier conflict. See `docs/ASSIGNMENT_VALIDATION.md`, `docs/MODEL_EVALUATION.json` and `docs/BROWSER_CHECKS.json`. Live evaluation remains pending credentials and model selection; no provider call or human approval is claimed.

## Start locally

Python 3.11 or later is required. From the extracted project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-tested.txt
python -m deallens.cli serve
```

Open **http://127.0.0.1:8765**. The package includes original PDFs and precomputed outputs, so serving does not need network access. On Windows, activate with `.venv\Scripts\activate`.

To reproduce the pipeline and tests:

```bash
python -m deallens.cli run
python -m unittest discover -s tests -v
python tests/evaluate_sources.py
PYTHONPATH=. python tests/evaluate_model.py
python -m deallens.cli ask bio_techne "What is the consideration per share?"
python -m deallens.cli ask organon "Is there a financing condition?"
python -m deallens.cli ask uber_delivery_hero "What financing arrangements are disclosed?"
```

`--strict` on `ask` requires human-verified records. The shipped run has none, so strict mode deliberately abstains. `run --threshold 0.99` blocks the current 0.97-score scalar rules. Confidence scores are heuristic scores, not calibrated probabilities. Use `--root /path/to/project` before the subcommand when running outside the project directory.

## What is included

| Area | Implementation | Material limitation |
|---|---|---|
| Ingestion | Original PDF bytes, SHA-256, timestamp, page text hashes, exhibit boundaries, OCR/sparse-page flags | External page completeness and actual filing dates unverified; no OCR engine |
| Extraction | Shared 42-field catalog; deterministic scalar rules; complex-clause candidate retrieval; exact page character locators | Only a subset has normalized supported values; confidence is uncalibrated |
| Comparison | Both layers preserved; exact/normalized comparison; conflicts block canonical values | Narrative equivalence unresolved; not-applicable is not inferred from absence |
| Timeline and risk | Evidence-linked events, date kinds and ten risk categories | Conditional/cross-page legal interpretations need review |
| Analytics | USD Bio-Techne case; local-currency validation slices; EUR bridge/FX sensitivity; four hedge strategies | Synthetic assumptions, constant DV01 and expiry payoffs; no live market pricing |
| QA | Twelve question categories; direct supported values or exact unsupported response | Does not turn keyword matches into legal answers |
| AI controls | Optional bounded Responses API extraction, strict schema, citation checks, request/usage audit, no tools or self-approval | Fake-transport tested; live quality and retrieval recall unmeasured |
| Audit | Versioned review decisions, immutable run folders, SQLite history and regenerated downstream outputs | Reviewer identity is locally self-attested, not authenticated |

## Architecture and source hierarchy

`ingest.py` creates canonical normalized page text and stable checksum/page/character locators. `extract.py` applies the same catalog and rules to each source, validates evidence, compares filing and agreement layers, and produces timeline events. `risk.py` attaches general analytical implications without treating candidates as established contract terms. `analytics.py` reads versioned assumptions and available source anchors. `qa.py` routes questions to evidence; it does not contain transaction answers. `storage.py` persists run lineage in SQLite. `server.py` serves a read-only loopback interface.

Relevant executed transaction or financing agreement takes precedence over the filing summary, followed by other exhibits. A hierarchy never deletes a conflict. Candidates with different wording remain unresolved until reviewed. Page numbers are physical PDF pages, starting at one. Section titles can be unresolved; exact page/character locators remain available. Whitespace is normalized before offsets are assigned; original PDFs are retained.

## Files and outputs

- `config/sources.json`: source URLs and development/validation roles; no extracted deal terms.
- `config/assumptions.json`: all financing, market, premium and scenario assumptions with origin descriptions.
- `data/sources/`: the three original supplied-source PDFs.
- `outputs/latest.json`: identifies the latest immutable run folder.
- Each run contains a manifest and per-deal `document.json`, `extractions.json`, `comparisons.json`, `timeline.json`, `risk_map.json`, `analytics.json`, `qa.json`, `exceptions.json`, `metrics.json` and `scenarios.csv`.
- `outputs/deallens.sqlite`: queryable run history. SQL examples are in `docs/audit_queries.sql`.
- `docs/TECHNICAL_MEMO.pdf`: three-page technical memo.
- `docs/CASE_REVIEW.md`: source-specific findings and review priorities.
- `docs/GENERALIZATION.md`, `docs/KNOWN_ISSUES.md`, `EXECUTION_PLAN.md`, `AGENT_WORKFLOW.md`: scope, evidence and implementation decisions.

## Financial conventions

For USD 4bn and supplied DV01 of USD 65,000 per USD 100mm, portfolio DV01 is USD 2.6mm/bp. A +25bp benchmark shock increases the first-order PV of financing cost by USD 65mm and annual coupon cost by USD 10mm. These are different measures and are never added together.

Debt is assumed priced at Treasury/benchmark plus issuer spread: 4.25% + 1.00% = 5.25% for the development case. The 4.40% swap rate implies a 15bp initial swap spread; adding it again to the debt coupon would double-count benchmark exposure. Payer swap receipts equal DV01 times the change in swap rate, which includes benchmark and swap-spread moves. Issuer spread remains unhedged. Assuming credit DV01 equals benchmark DV01 is explicit.

Positive net incremental cost is worse for the issuer. Option premiums and contingent fees are assumed upfront charges, not market quotes. An ordinary payer option can retain a payoff after deal failure; a synthetic deal-contingent swap cancels on failure with the fee retained. Actual documentation can differ. Delay scenarios use illustrative rolls/renewals, not repriced forward curves. Outcome-weighted costs use an explicitly specified joint rate/completion scenario and are not forecasts or recommendations.

## Adding another deal or a model

Add a document ID and HTTPS URL to the source configuration, or supply its PDF with that ID as its filename. Run the same pipeline. There are no company-specific answer branches in extraction or QA. The development role selects the assignment's required Bio-Techne synthetic inputs; all validation cases use the common template and supported currency.

The optional `run --model YOUR_MODEL_ID` path uses bounded clause retrieval and schema-constrained proposals. Configure `OPENAI_API_KEY` privately in your local environment; do not put it in source code or chat. Model proposals remain unverified until explicitly reviewed. The provider transport and review lifecycle are tested with synthetic fixtures, not a live model. See [MODEL_AND_REVIEW.md](docs/MODEL_AND_REVIEW.md) for commands, limits and review instructions.

## Before submitting

Read the technical memo and known issues. Run and evaluate semantic extraction, independently inspect the important source pages, all calculations and retained code, complete actual review decisions, validate fee/award completeness, and revise the agent log to include your actual work. A small fixture pass must not be presented as accuracy across the whole contract. The repository includes genuine implementation commits; do not invent human decisions or inflate time spent.

## Review package

`python docs/package_deliverables.py` creates `outputs/deliverables/DealLens_review_package.zip` with source, original PDFs, latest run JSON/CSV, SQLite history, matching review packet, memo, verification reports and a genuine Git history bundle. The package manifest hashes every included file. Credentials, virtual environments and unrelated files are excluded by explicit input selection. This is a review candidate while live extraction and human review remain outstanding.
