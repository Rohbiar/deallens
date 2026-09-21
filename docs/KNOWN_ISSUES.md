# Known issues and production roadmap

Current measurements are in [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md). Historical model reports describe their own runs; they are not current coverage claims.

## Remaining assignment limitations

1. Complete normalized interpretation of complex clauses is unfinished. Whole sections and selected references are now retained, but excerpts do not establish complete treatment of award cohorts, fee triggers, regulatory remedies or conditions. QA labels these responses partial and keeps normalized values null.
2. Section lookup is based on numbered headings. Unnumbered provisions, incorporated documents, nested references and definitions outside recognized dictionaries may remain unresolved. Cross-reference lookup is one hop, same-instrument and bounded. Full source pages remain authoritative.
3. The three PDFs match fresh publisher downloads. This establishes the downloaded snapshot, not completeness of omitted schedules or separate commitment/fee letters. Some bridge pricing components are visibly redacted and cannot be extracted from the supplied public record.
4. Organon and Uber filing dates are SEC-index-verified. Bio-Techne's date is reported by publisher PDF metadata; an accessible independent filing index was not obtained.
5. Comparisons resolve supported scalars but leave narrative equivalence unresolved. The Uber exact-price versus minimum-price difference remains visible and blocks its canonical answer.
6. Timeline expressions preserve contractual anchors and units, but conditional and business-day deadlines are not executable schedules. Uber's regulatory clocks are not forced into US merger extension scenarios.
7. All source fixtures and qualitative assessments are agent-curated. Contract-wide precision, recall and calibration are unmeasured. Validation documents informed shared improvements, so final results are adapted validation, not untouched holdouts.
8. No human-verified records are shipped. This does not imply that a nonexpert should provide nominal legal approval. The candidate remains responsible for the submission and its disclosed limitations.

## Financial scope

The scenario model uses constant DV01, synthetic forward reference levels, assumed premiums and linear roll/renewal costs. It has no yield/volatility curve valuation, convexity, early-unwind pricing or hedge-accounting model. These are disclosed prototype simplifications; live pricing is not necessary to demonstrate the assignment's scenarios.

The EUR bridge base pricing grid is extracted separately. Borrower rating, draw fraction and EURIBOR are not established by the agreement's grid. Public step-up sizes, funding fees and duration fees are redacted. Annualized interest by rating level is not a lifetime cashflow calculation. No termination fee is assumed available to offset hedge losses.

## Production work for confidential information

Use approved isolated infrastructure, authenticated deal-level permissions, encryption, private model endpoints, restricted egress, an approved retention contract and a secrets manager. Reapply document access controls at retrieval and output. Document text cannot authorize tools or external transmission. Add signed immutable audit records, attributed review and dual approval for material corrections or distribution. Trading remains outside this application.

Add reproducible environment locks, authenticated review, source-update monitoring, independent semantic benchmarks and exact financial valuation before operational use. These production features should not displace the remaining extraction and validation work for this case study.
