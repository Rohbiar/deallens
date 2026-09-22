# Agent workflow record

## Ownership and actual participants

The user delegated assignment review and project development to Codex. Early iterations were performed by one Codex assistant. The final structured-interpretation phase used coordinator-managed Codex work packages A through F for retrieval, structured interpretation, consumer integration, semantic challenge design, analytics reconciliation and final audit/documentation. The coordinator reviewed and integrated shared files. The exact underlying model identifiers for every agent were not independently recorded. Initial implementation used an in-memory test provider; later user-executed historical live runs used the models identified in their run manifests. The current final run is deterministic and made no provider calls.

The candidate reviewed the implementation, calculations, documentation and disclosed limitations and accepts responsibility for the submitted work. No independent legal verification, manual correction or hedge approval is claimed. All retained code and accompanying documentation were agent-generated and then inspected/tested as described below. The source fixture set and source review are agent-curated, not human ground truth.

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

No contemporaneous workstream timer was maintained, so the following figures are retrospective estimates reviewed by the candidate rather than stopwatch measurements.

| Workstream | Estimated candidate time |
|---|---:|
| Assignment review, source familiarization and planning | 1.5 hours |
| Architecture, ingestion and baseline extraction | 1.5 hours |
| Retrieval and structured interpretation | 2.0 hours |
| Financing and hedging analytics | 1.5 hours |
| Testing, debugging and source validation | 2.0 hours |
| UI, documentation and workflow records | 1.0 hour |
| Final review, memo and packaging | 1.0 hour |
| **Total** | **10.5 hours** |

Completing the same implemented scope without coding agents is estimated at approximately 30–40 hours. Against the 10.5-hour candidate estimate, this represents roughly 3–4x execution leverage, or approximately 20–30 hours of avoided implementation effort. The estimate excludes independent legal review and productionization, neither of which was completed. Per-document deterministic execution itself is measured in seconds in the recorded run outputs; that runtime is separate from development effort.

## Second iteration

The continuation implemented bounded provider requests, schema-constrained proposals, exact retrieved-citation checks, usage/request logs and explicit versioned reviewer decisions. Original runs are preserved and downstream outputs are regenerated. A control fix excludes rejected/superseded records from QA, comparisons, timelines and analytics. The suite now has 48 tests, including synthetic end-to-end review and fake HTTP transport cases. No live provider call or actual human review occurred.

Next: evaluate an approved live model, perform actual human review, model cross-references and party roles, and expand independently reviewed evaluation coverage. Then replace illustrative hedge and bridge assumptions with approved curves, pricing and contract-specific terms. Preserve the deterministic baseline to measure whether added complexity actually improves supported precision and recall.

## Third iteration: 2026-09-20 continuation

One Codex assistant continued locally; no subagents were used. Read the five requested project documents and the original `DealLens_Core_Case_Study_Editable.docx` in document order. Reinspected selected source pages for award cohorts, funding conditions, extensions, remedy elections, price qualifiers and fee tails. This is agent analysis, not human review.

The initial local test attempt failed because PyMuPDF was absent. Installed the pinned 1.26.6 dependency in the project virtual environment after network approval. Added regression tests before fixing preceding-context retrieval, malformed response handling and non-finite values; failures are preserved in `CONTINUATION_REGRESSION_BEFORE.txt`. A source retrieval audit found the ISO-currency price-floor miss; its failing regression is in `RETRIEVAL_REGRESSION_BEFORE.txt`. Revised the shared catalog without adding transaction-specific answers. The suite now passes 54 tests and 16 source fixtures. Bounded retrieval reaches the same 16 selected excerpts; this is not whole-document recall.

Ran HTTP checks and actual browser flows (dashboard, supported answer, strict abstention and Uber price conflict). Fixed the memo builder’s Linux-only font paths using ReportLab’s bundled fonts, rebuilt the three-page memo and visually inspected all three pages. Prepared requirement traceability, model evaluation and source-review scope records plus a review packet with no approvals. No workstream timer was kept at that stage; the final retrospective estimates appear in the Time and leverage section.

Live inference is pending: credentials were absent, and the user said they would configure them and specify a model. No API request or live performance result is claimed. The 54-test count includes synthetic model/reviewer cases only. The deliverable package remains a review candidate while live extraction and material human review remain outstanding.

## Live connection recovery: 2026-09-20

The user ran gpt-4.1-mini with a locally configured key. Run `20260920T161654Z-c7b3c412` selected hybrid extraction but recorded three connection errors and zero model proposals; it is not a successful live extraction run. An unauthenticated connection probe reproduced missing local issuer certificates in the macOS Python environment. Added Certifi to the dependency files and loaded its CA roots alongside default trust, without disabling certificate or hostname verification. Added specific safe TLS diagnostics and visible CLI warnings when live calls fail. All 56 tests pass. A credential-free probe through the updated transport reached OpenAI and received the expected HTTP 401, establishing TLS connectivity only, not credential validity or model access. The earlier review archive has not been refreshed; refresh after a successful live evaluation.

## First completed live evaluation

The user executed run `20260920T162331Z-957420e8` with their locally configured key. Inspected all 11 request outcomes and all five retained proposals. Four prices agree with cited evidence; the financing narrative was not a valid boolean for the review workflow. Six outputs were rejected, with exact causes unavailable for four because older audits stored only the exception class. Preserved the original run; added prompt v4 field contracts, scalar type validation, safe rejection reasons and distinct provider-error skip status. All 59 tests pass. No live execution of v4 and no actual human review occurred. See LIVE_EVALUATION.md; the earlier review archive awaits refresh.

## Prompt v4 live follow-up and refreshed handoff

The user executed run `20260920T163210Z-a5687251`. Assessed twelve completed responses: seven candidates (six non-null), three exact-citation rejections, two empty abstentions. Four prices and Bio-Techne financing=false agree with selected evidence. Flagged Uber financing=true as unsupported by clause 1.5 funding obligations; preserved the candidate and recorded a separate agent assessment, without using human review attestation or changing the immutable run. Tiny changed-budget samples do not prove overall quality improvement. Updated the three-page memo, current-run review packet and package. Complete semantic extraction and human review remain pending.

## Authorized budget and broader batch preparation

The user authorized a $10 testing budget. Added persistent SQLite reservations to CLI provider calls, counted separately before every HTTP attempt, with a $1 buffer for previous usage and billing uncertainty. No automatic release on failures, concurrent overspending, or unknown-price models is allowed. Verified current model prices from official documentation. Five spending-control tests bring the suite to 64 tests. An offline fake-transport plan sizes 76 requests across 15 common fields: $2.936138 reservation for single attempts, $8.808414 for three attempts each, excluding the $1 buffer. These are conservative reservations, not actual billed cost. No new paid API calls occurred; the key is still in the user terminal only. Prepared an executable batch script and per-request progress reporting for the user to launch.

## Broader batch continuation

Evaluated user-executed run 20260920T170013Z-4017a08d against selected original PDF clauses. Recorded material semantic errors without changing human review status. Added prompt v5 field contracts, operative borrowing-heading retrieval priority and safe differentiated citation diagnostics. All 66 unit/control tests and 16 scalar fixtures pass. No new paid request was made and v5 effectiveness is unmeasured. Prepared an undecided review packet and priority findings in docs/BROAD_BATCH_REVIEW.md.

## Requirements continuation after user clarification

The user explained that they are not qualified to certify legal interpretations. Removed instructions asking for nominal legal approval; retained expert-review limitations and technical ownership. Added nine common-rule party identities, ten disclosed agent annotations, offline regeneration preserving paid proposal history, refreshed/pinned browser runs and stale-source blocking. Added field-by-field requirement coverage and a demo/ownership guide. A synthetic adjacent-party test checks that definition delimiters are not consumed and alternate parties lost. HTTP validation initially hit sandbox restrictions, then an import-path error; the corrected loopback test passed. Seventy-three unit/control tests and 25 selected source fixtures pass. No new API calls were made by the assistant; a four-field live retest awaits execution in the user's credential-bearing Terminal. Workstream time and net savings remain unmeasured rather than retrospectively invented.

## Focused v5 evaluation and citation protocol recovery

User ran 18 focused calls. Retention fell from nine to six on the corresponding v4 request subset; no improvement claim is made. Ten responses failed exact quotation and one failed nested JSON validation. Source inspection still found modality, fee-trigger and field-scope errors. Added six record-bound agent assessments, without applying review decisions. Replaced quotation copying with request-specific passage IDs, mapped back to exact source text and validated by the existing integrity gate. Official Structured Outputs enum support was checked; schema compliance does not establish semantics. All 76 offline tests pass. The five-request v6 smoke test is planned at approximately $0.192 reserved before retries, but has not run. No paid call was made by the assistant.

## V6 citation smoke and typed-value recovery

User executed five remedy calls: four retained candidates, zero citation failures and one nested-JSON rejection. This provides narrow live evidence that passage selection works; it is not semantic validation. Agent inspection found wrong-field focus, missing qualifications and truncated definitions in retained proposals. Added four source-bound annotations without human promotion. V7 requests actual JSON scalar/null or a summary/details object instead of asking the model to escape JSON inside a string; an adapter preserves the internal record format. All 77 offline tests pass. No new assistant API calls and no v7 live results are claimed.

## V7 evaluation: format success is not semantic success

User executed five calls and all five passed value/citation validation. Agent inspection still found wrong-field summaries and prohibited-versus-not-required errors. Added five explicit source assessments and conservative automatic quality warnings without changing normalized values or human review status. All 79 unit/control tests pass. Repeating the same smoke was rejected as low value; future paid evaluation must follow substantive clause/definition and semantic changes. No new assistant API call was made.

## GPT-5.5 continuation and consolidation

User executed GPT-5.5 comparison and Organon retest in their credential-bearing Terminal. The agent inspected saved outputs and selected original-source clauses. A missing transport citation bound caused the initial Organon rejection; v8 aligned schema, prompt and local validation, and both retest requests passed. Source interpretation improvements and remaining qualifiers are recorded as agent annotations, never human approvals.

An offline consolidation selected Bio-Techne/Uber from 20260920T233813Z-64f21f5e and Organon from 20260920T234423Z-9b827d83. Run 20260921T034805Z-88a4e5cf preserves origin IDs, checks PDF hashes, requires matching assumptions/thresholds and retains the five unverified candidates. No paid request was made during consolidation. 82 tests, 25 selected source fixtures, requirement artifact checks and loopback HTTP checks passed. The HTTP test initially failed sandbox binding and succeeded after approved escalation. The updated memo was rendered and all three pages visually inspected. Full semantic coverage remains incomplete.


## Section-aware continuation on 2026-09-21

The user requested continued implementation toward submission readiness following a repository/specification gap assessment. Work was performed by the current Codex agent; no subagents or new paid model calls were used. Existing user changes and historical model outputs were preserved.

The initial section index missed Organon's headings because they contain a trailing decimal period; source inspection exposed zero indexed sections. The parser was corrected to accept both forms, with a regression test. A second inspection found RSU matching inside “pursuant” and cure inside “procure”; word-boundary rules and negative tests now prevent both. Full sections preserve the previously omitted Organon closing-time-condition exception and Parent-elected waiver. These are source-retention checks, not claims of complete interpretation.

A proposed completeness shortcut—counting every newly retrieved section as a fully answered legal field—was rejected. Excerpts keep null normalized values, a separate status and partial QA; strict human-verification mode still abstains. The interface exposes references and selected definitions for review. Source excerpts require a deliberate normalized correction rather than nominal approval.

Source review located a public six-level bridge pricing grid and redacted step-up, duration-fee and funding-fee amounts. The analysis now separates the disclosed grid from synthetic draw and EURIBOR assumptions, and does not fill redactions. All three publisher downloads matched the stored bytes; Organon and Uber filing dates were verified against SEC indexes. Bio-Techne's inaccessible index remains a limitation, with its PDF-metadata date explicitly labeled.

Current measured checks and coverage are in docs/SUBMISSION_STATUS.md. No independent human semantic review, calibrated accuracy, or net time saving is claimed. The original ten substantive decision records above remain the representative workflow record; this continuation documents subsequent recovery and implementation.

## Final structured implementation wave

The user explicitly requested agent work packages for the remaining development. The work was divided as follows:

| Package | Role | Retained result |
|---|---|---|
| A | Retrieval dependencies | Bounded recursive same-instrument context graph, stable source/section IDs, cycles, ambiguity and budget state |
| B | Structured interpretation | Versioned atomic terms for extensions, fees, remedies, awards and financing conditions, with fail-closed validation |
| C | Structured consumers | QA, comparisons, timelines, risk views and escaped browser rendering for supported and unresolved components |
| D | Independent challenge | Frozen agent-curated set of 72 supported atomic assertions and four intentionally unresolved cases |
| E | Analytics reconciliation | Facts-to-scenario boundary, funding-condition roles and a neutral transaction-failure scenario |
| F | Requirement closure | Read-only gap audit followed by current status, workflow, reproducibility and packaging documentation |

The coordinator owned shared CLI, server, storage, semantic-prediction and run-generation changes. Work-package reports disclose their bounded scope and test evidence. This was real multi-agent delegation; it is not a claim of independent human review.

## Coordinator corrections during integration

Three material integration defects were found and corrected before the final run:

1. A generic named-party fee expression captured a stray preceding word under case-insensitive matching. The parser was made locally case-sensitive without adding transaction names to production logic.
2. Statement-level unresolved dependencies were initially ignored by the analytics support gate. The gate now combines term- and statement-level unresolved items, preventing an incomplete statement from driving scenarios.
3. The Uber award selector initially chose a generic treatment passage rather than the bounded settlement-efforts clause. The generic selector was corrected and protected with source-backed tests.

The semantic adapter was intentionally kept status-aware. Because all 14 current structured terms remain candidates, it emits unresolved predictions instead of copying candidate content into supported assertions. On the frozen set, zero assertions were made, all 72 supported assertions were unresolved, bounded precision was null, bounded recall was zero, and all four source-unresolved cases were respected. This is a conservative control result, not successful semantic accuracy.

## Final measured state

The integrated code is commit `defe4a3`; deterministic run `20260922T024418Z-d989f939` contains 14 structured candidate terms and 34 statements. The suite passes 179 tests, 25/25 selected scalar/source fixtures and 18/18 provision fixtures. Across 36 required QA combinations there are 12 supported, 22 partial, one conflicted and one review-required result. Zero records or terms are human-verified, and the final wave made no paid provider calls.

The final 10.5-hour candidate-time and 3–4x leverage figures are retrospective estimates, not contemporaneous measurements. Rohit retains final ownership of the calculations, code, disclosures and submission decision.
