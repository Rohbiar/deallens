# Generalization assessment

## What was actually evaluated

One Python/SQLite application processes all three PDFs. Bio-Techne was the first executed development run. All three sources were briefly inspected before that run to understand the assignment's required structures, so the validation sources were not a pristine unseen holdout. After the first three-document run, common rules were extended for consideration definitions, explicit financing-condition language, fee terminology, thresholds and exact/minimum qualifiers. Results after those changes are adapted validation results, not untouched out-of-sample accuracy.

## Results

| Document | PDF pages | Supported field types | Total catalog fields | Human verified records |
|---|---:|---:|---:|---:|
| Bio-Techne | 99 | 12 | 42 | 0 |
| Organon | 109 | 11 | 42 | 0 |
| Uber and Delivery Hero | 149 | 14 | 42 | 0 |

Execution times are measured in each run's `metrics.json`, with current values recorded in `docs/PIPELINE_RESULTS.txt` (earlier runs took approximately 4–6 seconds per source). A field type counts as supported if at least one layer contains a supported record; this does not establish that its canonical comparison is resolved or that all subfields are complete. Candidate and not-found records remain in the outputs.

The 25 selected source fixtures pass, including nine party-identity checks. They were curated by the same agent through direct source inspection, not an independent human assessor. They test selected prices, qualifiers, signing/outside dates, financing conditions and fee/financing amounts. Neither this result nor exact citation matching estimates semantic accuracy across the full agreements. Full accuracy remains unmeasured.

## What generalized

- PDF ingestion, checksums, source/page identity, SQLite lineage and export formatting.
- Separation of filing summary, transaction agreement, financing agreement and other exhibits.
- Transaction classification distinguishing a German public takeover offer from mergers.
- USD and EUR normalization, including German-style day-month-year dates.
- Shared date, price, fee and explicit no-financing-condition patterns.
- Common financial sensitivities with separately labeled local-currency assumptions.
- Unsupported-answer and conflict behavior, including a real exact-price-versus-price-floor difference.

## Required extensions and remaining failures

| Issue | General model change | Current state |
|---|---|---|
| Exact price versus minimum price | `value_qualifier` on monetary facts and comparison keys | Implemented; Uber comparison requires review |
| Financing floor versus facility commitment | Separate `committed_financing_minimum` field | Implemented; avoids falsely conflicting EUR 11.5bn with EUR 14.2bn |
| Grant-year award cohorts | Typed grant cutoff, vesting status, performance basis and payment timing | Candidate retrieval only; structured cohort extraction pending |
| Elective extension changes remedies | Event graph with actor, notice, preconditions and covenant effects | Preserved in source review; engine does not fully encode it |
| Tender mechanics and attributed holdings | Explicit denominator, inclusion/exclusion rules and multiple acceptance periods | Threshold source text preserved; complete structured mechanics pending |
| Regulatory deadlines versus long-stop | Separate regulatory deadline, authorized extension and completion/termination clocks | Timeline candidates available; US-style extension scenarios blocked for Uber |
| Bridge fees and lending conditions | Rating grid, relative fee schedule, borrowing conditions and day-count model | Candidate evidence plus clearly synthetic bridge sensitivity |
| Ambiguous party labels | Layer-specific issuer, target, parent, bidder, guarantor and fee payer/payee roles | Operative target, parent/bidder and vehicle names extracted; guarantor scope and full cross-layer party graphs remain unresolved |

## Architecture improvements

Use clause/definition graphs before extending regex coverage further. The optional bounded model path includes neighboring-page retrieval, schema validation and exact-citation checks, and a versioned reviewer workflow is implemented. Limited two-field live evaluation is documented in LIVE_EVALUATION.md; comprehensive model quality and actual human review remain unestablished. Build a separate labeled validation corpus containing negative and conflicting examples, freeze extraction rules, and evaluate complete fields with precision, recall and abstention. Preserve the current deterministic rule suite as a transparent baseline and regression gate.

## Continuation retrieval evaluation

The model retriever initially missed Uber’s agreement price floor because its consideration pattern recognized currency symbols but not ISO currency labels. A shared ISO-currency rule and preceding-chunk context fixed the selected retrieval miss. `MODEL_EVALUATION.json` reports 16/16 selected scalar excerpts reachable within the 16,000-character budget. This is adapted, agent-curated validation; it does not establish full-clause recall or live semantic accuracy. All 54 tests pass; live provider calls and human approvals remain zero.

Latest live follow-up: prompt v4 produced seven retained candidates from twelve responses, including one null and an unsupported Uber financing inference. Full legal extraction accuracy remains unmeasured. See LIVE_EVALUATION.md for the current result; earlier counts above are historical.

## Current continuation

The broader 76-response live batch is documented in BROAD_BATCH_REVIEW.md. Shared introductory-party rules now support nine additional field/document identities without source-specific names in code. Retrieval prioritizes operative party and borrowing headings. Agent annotations identify ten historical candidate errors without applying human decisions. The current 73 tests and 25 fixtures concern controls and selected values, not full semantic accuracy. Earlier counts above record prior development stages.
