# Agent workflow record

## Ownership and actual participants

The user delegated assignment review and project development to Codex. A single Codex assistant performed source reading, implementation, tests and documentation. No subagents or external coding agents were used. The exact underlying model identifier was not independently verified in the runtime. The application's live model field is null because no live inference provider was connected. An in-memory test provider was used solely for adapter tests.

Rohit has not yet reviewed or approved this implementation. No human legal verification, manual correction or hedge approval is claimed. All retained code and accompanying documentation were agent-generated and then inspected/tested as described below. The source fixture set and source review are agent-curated, not human ground truth.

## Representative context and instructions

The complete DOCX assignment was extracted in original document order. The three specified URLs were downloaded as PDF bytes. Design context emphasized common schema and code, source/assumption/analysis separation, no hard-coded transaction answers, failure-safe extraction, party/condition differences, financial sign conventions and an honest Git history. Additional context was supplied through focused readings of date definitions, extension clauses, award provisions, financing obligations and fee sections.

## Substantive decision records

| Record | Observation and decision | Evidence or outcome |
|---|---|---|
| 1 Successful delegation | The user delegated document review and development. Codex built a shared ingestion-to-analytics pipeline rather than asking the user to implement it. | Working source code, original PDFs, machine-readable outputs and a local interface. This is user-to-agent delegation, not a claim of subagent work. |
| 2 Rejected design recommendation | During design, grouping options and deal-contingent swaps as one strategy was rejected. They have materially different failure payoffs and fees. | Four separate strategy implementations and tests showing ordinary option payoff can survive transaction failure. This was an internal design alternative, not advice from a fictitious second agent. |
| 3 Incorrect environment assumption | The first download script assumed `requests` was installed; it was not. | `ModuleNotFoundError` led to replacing it with standard-library `urllib.request`. All three PDFs then downloaded successfully. |
| 4 Retrieval recovery | The Organon URL failed in the web reader, but the original PDF could be downloaded directly. | Original URL retained; no substituted source or invented content. |
| 5 Incorrect extraction assumption | A broad agreement-date rule treated a Clean Team Agreement date as a competing merger date. | Bio-Techne development output exposed the conflict. Restricted rules to transaction agreement titles and retained a regression test. |
| 6 Revision after failed test | The initial outside-date pattern missed an intervening proviso before the defined term. | `test_initial_outside_date_with_proviso` failed, then passed after a general grammar change. No deal-date literal was added to extraction code. |
| 7 Debugging episode | The model proposal adapter initially contained a mismatched list bracket, preventing test import. | Fixed syntax, then ran the full test suite; the genuine failure was not hidden as a successful run. |
| 8 Context improvement | Focused source inspection distinguished Organon's Parent-elected remedy waiver and grant-year awards from generic merger terms. | Recorded in CASE_REVIEW.md and known limitations; deliberately did not claim that the parser fully models those legal state transitions. |
| 9 Financial and semantic correction | Further Uber source review identified an exact-price versus minimum-price distinction and a financing floor distinct from bridge commitment. | Added common monetary qualifiers, comparison gates and a separate financing-minimum field. A regression test blocks false normalized matches. |
| 10 Rejected completeness claim | Keyword retrieval and exact source offsets do not prove full legal extraction. | Complex normalized values remain null; full accuracy is unmeasured; no human records are marked verified. |

## Generated changes retained and materially revised

Retained ingestion, common catalog, scalar extraction, comparison, timeline, risk mapping, SQLite schema, analytic functions, QA router, model boundary and read-only UI. Revised ancillary-date parsing, outside-date grammar, currency/qualifier comparison and field-coverage counting. Added source-grounded negative/qualification tests rather than relying on successful execution alone.

The only case-specific analytics selection chooses the assignment's required synthetic Bio-Techne assumptions using its configured development role. Validation analytics use the same template and supported currency. Source-specific observations live in review documents and test fixtures, not as answers hidden behind the QA interface.

## Testing and validation loops

1. Execute Bio-Techne development run, inspect supported fields and conflicts.
2. Run financial identities and negative extraction tests; fix actual failures.
3. Execute the same pipeline on all three documents and inspect classification, layers and currency adaptation.
4. Extend common rules after validation feedback; explicitly disclose that these are adapted validation results.
5. Validate exact page/character evidence for every retained excerpt.
6. Run 27 unit/control tests and 16 selected source fixtures; preserve output in `docs/TEST_RESULTS.txt` and `docs/SOURCE_EVALUATION.json`.
7. Validate local interface behavior and technical memo rendering; see the packaged verification results for actual outcomes.

## Time and leverage

The assignment's 8–12-hour estimate is a planning budget, not claimed time spent. Per-document execution is measured in run outputs, approximately 4–6 seconds per document in the recorded full runs. Git timestamps identify actual implementation stages; no retroactive commits or invented work sessions were created. No reliable workstream timer was kept, so workstream effort and net time saved are not quantified. Human review and the remaining semantic extraction work have not occurred. Agent leverage is demonstrated by working artifacts and verification, not an invented percentage or hour estimate.

## Second iteration

The continuation implemented bounded provider requests, schema-constrained proposals, exact retrieved-citation checks, usage/request logs and explicit versioned reviewer decisions. Original runs are preserved and downstream outputs are regenerated. A control fix excludes rejected/superseded records from QA, comparisons, timelines and analytics. The suite now has 48 tests, including synthetic end-to-end review and fake HTTP transport cases. No live provider call or actual human review occurred.

Next: evaluate an approved live model, perform actual human review, model cross-references and party roles, and expand independently reviewed evaluation coverage. Then replace illustrative hedge and bridge assumptions with approved curves, pricing and contract-specific terms. Preserve the deterministic baseline to measure whether added complexity actually improves supported precision and recall.
