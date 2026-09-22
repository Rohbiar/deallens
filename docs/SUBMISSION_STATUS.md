# Submission status

Current run: `20260922T024418Z-d989f939` at code commit `defe4a3`. This is a runnable submission candidate with explicit semantic limitations, not a claim of complete extraction. This deterministic run made no provider calls and contains zero human-verified records.

| Transaction | Supported field types | Section-excerpt fields | Structured candidates | Fully supported questions | Partial questions | Filing date |
|---|---:|---:|---:|---:|---:|---|
| bio_techne | 12/42 | 21 | 4 | 5/12 | 7/12 | 2026-06-26 (pdf_metadata_reported) |
| organon | 11/42 | 18 | 5 | 4/12 | 8/12 | 2026-04-27 (sec_index_verified) |
| uber_delivery_hero | 15/42 | 21 | 5 | 3/12 | 7/12 | 2026-07-16 (sec_index_verified) |

Across the 36 required transaction/question combinations there are 12 supported answers, 22 partial answers, 1 review-required answer and 1 conflicted answer. The run contains 14 candidate structured terms with 34 atomic statements; 0 are machine-supported or human-verified. Candidate terms enrich explanations but do not promote QA answers or drive analytics.

## Final implementation state

- Numbered provisions carry a bounded recursive dependency graph with stable source and section IDs, cycle detection, instrument boundaries, and explicit missing, ambiguous and budget-limited context.
- Versioned structured candidates cover extensions, fees, remedies, award cohorts and disclosed financing conditions. Actors, modalities, triggers, conditions, exceptions, timing, amounts and evidence remain separate.
- Structured candidates are persisted in JSON and SQLite and exposed in QA, comparisons, timelines, risk views, CLI and server responses. The browser labels uncertainty and never represents an election or conditional event as having occurred.
- Analytics include a neutral zero-rate transaction-failure scenario. Directional failure stresses remain additional sensitivities. Only validated supported terms without material unresolved items may drive structured dates; the current candidates do not.
- The model-request adapter and displayed QA evidence use the same retrieval graph, with downstream omissions disclosed. No transaction-specific names, dates, amounts or section numbers were added to generic interpretation logic.

## Verification

- 179 automated unit/control tests pass.
- 25/25 selected scalar/source fixtures pass.
- 18/18 selected provision/qualifier fixtures pass, and all attached context citations match their normalized source pages.
- The frozen agent-curated semantic set contains 72 supported atomic assertions and four deliberately unresolved source cases. The current candidate-only system asserted 0: 72 are reported unresolved, bounded precision is null, bounded recall is 0.0, and 4/4 source-unresolved cases were respected.
- Required Bio-Techne scenarios include the neutral `failure` scenario, both extension scenarios and the four specified rate/credit stresses.

These results establish artifact integrity, selected source retention and fail-closed behavior. They do not establish contract-wide legal precision or recall.

## Remaining limitations

All structured terms remain unreviewed candidates because their dependency graphs retain material or unknown unresolved context. Bio-Techne's filing date remains PDF-metadata-reported. The supplied record omits the Bio-Techne approval-jurisdiction schedule and an Organon PSU schedule exception; Uber's ultimate award treatment remains consent- and award-term-dependent, and public bridge step-up, duration-fee and funding-fee amounts are redacted. Exact citations prove provenance, not interpretation.

No human legal verification, live market valuation or authenticated production approval is claimed. The candidate must understand and accept the code, calculations and disclosed limitations before submission.

## Evidence and deliverables

See [requirement audit](REQUIREMENTS_AUDIT.json), [bounded semantic evaluation](SEMANTIC_EVALUATION.json), [source evaluation](SOURCE_EVALUATION.json), [provision evaluation](PROVISION_EVALUATION.json), [known issues](KNOWN_ISSUES.md), [technical memo](TECHNICAL_MEMO.pdf), and [demo guide](DEMO_GUIDE.md). The review archive must be rebuilt after the final memo so its manifest and extracted smoke checks describe this run.
