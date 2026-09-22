# Generalization assessment

One Python/SQLite application processes all three sources. Bio-Techne was the development case; Organon and Uber / Delivery Hero informed later shared improvements, so the final results are adapted validation results rather than pristine holdouts.

## Current measured result

| Document | Pages | Supported field types | Section-excerpt fields | Structured candidates | Human-verified records |
|---|---:|---:|---:|---:|---:|
| Bio-Techne | 99 | 12/42 | 21 | 4 | 0 |
| Organon | 109 | 11/42 | 18 | 5 | 0 |
| Uber / Delivery Hero | 149 | 15/42 | 21 | 5 | 0 |

The shared pipeline passes 25/25 selected scalar/source fixtures and 18/18 provision fixtures. Across the required 36 QA combinations, 12 are supported, 22 partial, one conflicted and one review-required. These denominators are bounded coverage measurements, not contract-wide accuracy.

The frozen agent-curated semantic set contains 72 supported atomic assertions and four source-unresolved cases. Because the current structured records are all candidates, the semantic adapter makes zero assertions: precision is null, recall is zero, all 72 supported assertions are unresolved and all four source-unresolved cases are respected.

## What generalized

- PDF ingestion, hashes, page identity, filing/exhibit layers and transaction classification.
- USD and EUR values, US mergers and a German public takeover offer.
- Stable scalar evidence plus full numbered provisions across continuation pages.
- Bounded recursive same-instrument references and definitions with cycles, ambiguity, missing targets and budget state.
- A common structured schema for actors, modalities, triggers, conditions, exceptions, timing, amounts and source IDs.
- Candidate interpretations for extension, fee, remedy, award and financing-condition families.
- Structured comparison, timeline, risk and QA consumers that preserve uncertainty and escape source/model text.
- A common financial engine with neutral failure, separate directional failure stresses and safely blocked dates.

Generic parsing contains no transaction names, transaction-specific section numbers, dates or amounts. Specific expected values remain in source-attributed fixtures and semantic descriptors.

## Schema extensions and remaining failures

| Issue | General extension | Current state |
|---|---|---|
| Exact price versus minimum price | Monetary qualifier in comparison identity | Implemented; Uber remains conflicted |
| Financing floor versus facility commitment | Separate financing-minimum field | Implemented |
| Automatic versus elective extension | Actor, modality, notice, conditions and caps | Candidate structured terms |
| Regulatory remedy limits | Required/permitted/prohibited action plus exceptions | Candidate structured terms |
| Grant-year and performance cohorts | Cohort selector, performance basis and timing | Candidate structured terms; omitted schedule remains open |
| Financing conditions | Transaction, lender and funding-source scenario roles | Candidate terms; no condition is deemed satisfied |
| Bridge pricing and redactions | Disclosed grid separated from synthetic use | Implemented; redacted fees remain unavailable |
| Tender and regulatory mechanics | Transaction classification and conditional clocks | Partial; no forced US-merger equivalence |

## Recommended next architecture steps

Freeze this deterministic baseline before changing interpretation policy. A future iteration should obtain qualified review for complete fields, govern a larger independent benchmark, improve recognition of unnumbered and incorporated material, and measure supported precision/recall after review. Live model proposals should remain a candidate source behind the same evidence graph and approval boundary, not a substitute for those steps.
