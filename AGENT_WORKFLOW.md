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

## Third iteration: 2026-09-20 continuation

One Codex assistant continued locally; no subagents were used. Read the five requested project documents and the original `DealLens_Core_Case_Study_Editable.docx` in document order. Reinspected selected source pages for award cohorts, funding conditions, extensions, remedy elections, price qualifiers and fee tails. This is agent analysis, not human review.

The initial local test attempt failed because PyMuPDF was absent. Installed the pinned 1.26.6 dependency in the project virtual environment after network approval. Added regression tests before fixing preceding-context retrieval, malformed response handling and non-finite values; failures are preserved in `CONTINUATION_REGRESSION_BEFORE.txt`. A source retrieval audit found the ISO-currency price-floor miss; its failing regression is in `RETRIEVAL_REGRESSION_BEFORE.txt`. Revised the shared catalog without adding transaction-specific answers. The suite now passes 54 tests and 16 source fixtures. Bounded retrieval reaches the same 16 selected excerpts; this is not whole-document recall.

Ran HTTP checks and actual browser flows (dashboard, supported answer, strict abstention and Uber price conflict). Fixed the memo builder’s Linux-only font paths using ReportLab’s bundled fonts, rebuilt the three-page memo and visually inspected all three pages. Prepared requirement traceability, model evaluation and source-review scope records plus a review packet with no approvals. No workstream timer was kept and no leverage/time-saved estimate is asserted.

Live inference is pending: credentials were absent, and the user said they would configure them and specify a model. No API request or live performance result is claimed. The 54-test count includes synthetic model/reviewer cases only. The deliverable package remains a review candidate while live extraction and material human review remain outstanding.

## Live connection recovery: 2026-09-20

The user ran gpt-4.1-mini with a locally configured key. Run `20260920T161654Z-c7b3c412` selected hybrid extraction but recorded three connection errors and zero model proposals; it is not a successful live extraction run. An unauthenticated connection probe reproduced missing local issuer certificates in the macOS Python environment. Added Certifi to the dependency files and loaded its CA roots alongside default trust, without disabling certificate or hostname verification. Added specific safe TLS diagnostics and visible CLI warnings when live calls fail. All 56 tests pass. A credential-free probe through the updated transport reached OpenAI and received the expected HTTP 401, establishing TLS connectivity only, not credential validity or model access. The earlier review archive has not been refreshed; refresh after a successful live evaluation.

## First completed live evaluation

The user executed run `20260920T162331Z-957420e8` with their locally configured key. Inspected all 11 request outcomes and all five retained proposals. Four prices agree with cited evidence; the financing narrative was not a valid boolean for the review workflow. Six outputs were rejected, with exact causes unavailable for four because older audits stored only the exception class. Preserved the original run; added prompt v4 field contracts, scalar type validation, safe rejection reasons and distinct provider-error skip status. All 59 tests pass. No live execution of v4 and no actual human review occurred. See LIVE_EVALUATION.md; the earlier review archive awaits refresh.

## Prompt v4 live follow-up and refreshed handoff

The user executed run `20260920T163210Z-a5687251`. Assessed twelve completed responses: seven candidates (six non-null), three exact-citation rejections, two empty abstentions. Four prices and Bio-Techne financing=false agree with selected evidence. Flagged Uber financing=true as unsupported by clause 1.5 funding obligations; preserved the candidate and recorded a separate agent assessment, without using human review attestation or changing the immutable run. Tiny changed-budget samples do not prove overall quality improvement. Updated the three-page memo, current-run review packet and package. Complete semantic extraction and human review remain pending.

## Authorized budget and broader batch preparation

The user authorized a $10 testing budget. Added persistent SQLite reservations to CLI provider calls, counted separately before every HTTP attempt, with a $1 buffer for previous usage and billing uncertainty. No automatic release on failures, concurrent overspending, or unknown-price models is allowed. Verified current model prices from official documentation. Five spending-control tests bring the suite to 64 tests. An offline fake-transport plan sizes 76 requests across 15 common fields: $2.936138 reservation for single attempts, $8.808414 for three attempts each, excluding the $1 buffer. These are conservative reservations, not actual billed cost. No new paid API calls occurred; the key is still in the user terminal only. Prepared an executable batch script and per-request progress reporting for the user to launch.
