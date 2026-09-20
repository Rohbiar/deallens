# Known issues and production roadmap

## Submission blockers

1. Full semantic extraction and validation are unfinished. The current baseline supports 8–11 distinct field types per document; many of the 42 catalog fields remain candidates or not found. Do not describe this as complete extraction.
2. The bounded, schema-constrained provider integration is implemented and fake-transport tested, but no live model extraction has been evaluated. Retrieval recall, semantic accuracy and dollar costs remain unmeasured; token usage is logged when returned.
3. Human review remains outstanding. A versioned CLI approve/correct/reject workflow exists, but reviewer identity is only locally self-attested. No shipped record is human-verified; the browser interface remains read-only.
4. Source-specific award cohorts, all fee triggers/tails, remedy limitations, cross-references, acceptance mechanics and lending conditions require complete clause-level reconciliation. Candidate windows can cut across page boundaries; read adjacent original pages.
5. Agreement-versus-summary narrative matches are unresolved, and summary-only fees may not be normalized from the agreement. Absence is not “not applicable” or a zero termination fee.
6. The date-kind classifier is heuristic. A page can contain several dates and conditions. Uber's regulatory timing should be represented as its own event structure rather than forced into US-style first/final outside-date extensions. Those extension scenarios are blocked in the baseline.

## Engineering and data limitations

- Actual filing dates are null until verified from filing-index metadata. Event and signature dates are preserved separately. Document title does not prove filing date.
- Text checksums find exact duplicates, not near duplicates. Missing internal pages can be detected when an independent expected count is supplied; otherwise completeness is unknown. Sparse pages may be intentionally blank rather than OCR failures.
- Sources are filing snapshots; subsequent amendments and deal developments have not been checked. Public document content can contain redactions and omitted schedules; jurisdiction lists may therefore be incomplete.
- Section detection is approximate. Stable physical page/character locators are authoritative. The extractor's `normalize` function changes whitespace, so offsets refer to normalized text, not PDF bytes.
- Source and assumption hashes are recorded, but installed dependency pins and execution environments need stronger reproducibility controls for production.
- Candidate retrieval uses a fixed maximum per field/layer. It is a navigation aid, not an exhaustive contract parser. No ranked retrieval recall has been established.
- Only a small manually inspected fixture set is evaluated. Citation validity and field coverage are distinct from semantic accuracy. No production accuracy percentage is available.
- UI HTTP routes and embedded JavaScript syntax pass checks, but full browser execution and visual layout were not verified because the required browser download timed out.

## Financial limitations

- No full yield curve, volatility surface, option valuation, convexity, credit term structure, carry, hedge accounting, collateral or capital modeling.
- Validation funding sizes and fixed-rate terms are synthetic illustrative slices. The EUR bridge disclosure is a maximum commitment, not proof of full drawdown or the same exposure as a seven-year refinancing.
- Bridge costs use synthetic rating/margin/step-up assumptions; actual grids, funding/duration/commitment fees and day counts are not priced. Annualized sensitivities are not bridge lifetime cashflow estimates.
- Delay costs are synthetic linear roll/renewal sensitivities. Extension-condition satisfaction is not established. Failure P&L is evaluated at a common modeled expiry; earlier failure requires a real valuation model.
- No source termination fee is netted against hedge unwind. Recipient identity, payment conditions, timing and actual collectability matter.

## Production changes for material non-public information

Use an approved isolated deployment with identity-based access, least-privilege service roles, deal-level document permissions, encryption, private endpoints, restricted egress and an approved model/data-retention contract. Reapply source access controls at retrieval and answer generation. Separate ingestion, model inference, reviewer approval and analytics services. Remove arbitrary external URL access; ingest only allowlisted repositories. Document text cannot authorize tools or external transmission.

Add an immutable signed audit log, reviewer attribution, dual approval for material corrections, retention rules and redaction handling. Keep credentials in the firm's secret manager. Require authorized human approval for any external distribution or hedge recommendation; trade execution remains outside this research application. Log evidence/chunk/prompt/model versions without putting sensitive text in unrestricted telemetry.

## Next implementation sequence

1. Run and evaluate an approved model using the implemented bounded extraction path and common catalog.
2. Add cross-page clauses, referenced-definition expansion, party-role graphs, award cohorts and typed deadline expressions.
3. Complete actual reviewer decisions using versioned runs; add authenticated identities and dual approval for production.
4. Build an independently reviewed gold set covering every critical field and diverse negative/conflict cases; quantify precision, recall and abstention.
5. Add actual curves, option pricing, FX forwards and exact bridge cashflows; test against independent pricing tools.
6. Add provenance signatures, reproducible dependency lock/container, authentication and deployment controls.
