# Generalization assessment

## What was actually evaluated

One Python/SQLite application processes all three PDFs. Bio-Techne was the first executed development run. All three sources were briefly inspected before that run to understand the assignment's required structures, so the validation sources were not a pristine unseen holdout. After the first three-document run, common rules were extended for consideration definitions, explicit financing-condition language, fee terminology, thresholds and exact/minimum qualifiers. Results after those changes are adapted validation results, not untouched out-of-sample accuracy.

## Results

| Document | PDF pages | Supported field types | Total catalog fields | Human verified records |
|---|---:|---:|---:|---:|
| Bio-Techne | 99 | 9 | 42 | 0 |
| Organon | 109 | 8 | 42 | 0 |
| Uber and Delivery Hero | 149 | 11 | 42 | 0 |

Execution times are measured in each run's `metrics.json`, approximately 4–6 seconds per source in this environment. A field type counts as supported if at least one layer contains a supported record; this does not establish that its canonical comparison is resolved or that all subfields are complete. Candidate and not-found records remain in the outputs.

The 16 selected source fixtures pass. They were curated by the same agent through direct source inspection, not an independent human assessor. They test selected prices, qualifiers, signing/outside dates, financing conditions and fee/financing amounts. Neither this result nor exact citation matching estimates semantic accuracy across the full agreements. Full accuracy remains unmeasured.

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
| Ambiguous party labels | Layer-specific issuer, target, parent, bidder, guarantor and fee payer/payee roles | Entity-role extraction pending; no silent cross-layer alias equivalence |

## Architecture improvements

Use clause/definition graphs and cross-page retrieval before extending regex coverage further. Connect a schema-constrained model adapter with exact-evidence validation and a reviewer workflow. Build a separate labeled validation corpus containing negative and conflicting examples, freeze extraction rules, and evaluate complete fields with precision, recall and abstention. Preserve the current deterministic rule suite as a transparent baseline and regression gate.
