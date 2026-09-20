# Assignment validation and handoff

Status: **review candidate; not complete semantic extraction or human sign-off**.

The original `DealLens_Core_Case_Study_Editable.docx` was read in document order on 2026-09-20. Its extracted requirements and checksum are retained in `ASSIGNMENT_REQUIREMENTS.txt`. This assessment is agent-authored. No requirement is considered satisfied merely because an output file exists.

| Assignment workstream | Evidence delivered | Assessment and remaining gap |
|---|---|---|
| 1. Ingestion and classification | Three original PDFs; per-run document/page/chunk inventories and hashes; 99, 109 and 149 pages; merger/takeover classification | Implemented with limits. Filing dates and external page completeness remain unknown. OCR need is flagged; no OCR engine is provided. |
| 2. Structured extraction | Common 42-field catalog, source locators, null/candidate/conflict handling | Partial: 9, 8 and 11 machine-supported field types. Parties, award cohorts, fee triggers/tails and other complex fields are not completely normalized. |
| 3. Summary/agreement comparison | Both layers retained; exact/normalized and qualifier comparisons; conflicts block canonical values | Scalar comparisons implemented. Narrative equivalence unresolved; absence is not not-applicable. Uber exact/minimum price difference retained. |
| 4. Timeline and risk map | Evidence-linked dates, candidate conditions, risk categories | Partial: date kinds are heuristic. Organon actor-dependent remedy change and Uber regulatory/long-stop clocks require structured semantic review. |
| 5. Financing and hedging | Bio-Techne synthetic USD 4bn case; four strategies; rate, basis, credit, failure and delay scenarios; adapted USD/EUR slices, FX and bridge sensitivities | Reproducible illustrative analysis. All supplied assumptions are labeled; no live derivative pricing. Validation funding sizes/fees are synthetic. |
| 6. Grounded QA | Read-only browser and CLI; twelve categories; exact unsupported response; strict review gate | Works for supported fields and partial answers. Many required complex questions abstain or remain partial. This is not full question coverage. |
| 7. Generalization | Same code on all three sources; GENERALIZATION.md; selected fixture and retrieval reports | Adapted validation, not pristine holdout. Full extraction precision/recall unmeasured. |
| 8. Controls/audit | SQLite history, immutable run folders, evidence checks, review queue, versioned decisions, model request audit | Implemented locally with limitations. Human identity is self-attested; no authenticated approval. Limited two-field live evaluation complete; one retained interpretation is unsupported. Full semantic validation remains outstanding. |
| Coding-agent workflow | EXECUTION_PLAN.md, AGENT_WORKFLOW.md, genuine Git history and failing/passing regression evidence | Agent actions and failures disclosed. No reliable workstream timer or invented time-saved estimate. Candidate retains ownership. |
| Final deliverables | Source/setup, original PDFs, machine outputs, timelines, CSV scenarios, UI, three-page memo, tests, audit and review packet | Prepared as a review package. Submission readiness remains blocked by semantic completeness and actual human review. |

## Verification performed

- 59 unit/control tests pass, including TLS trust, typed proposal and audit diagnostics.
- 16 selected scalar source fixtures pass. They were curated by the same agent and do not estimate contract-wide accuracy.
- Bounded retrieval initially reached 15/16 selected excerpts. The shared ISO-currency correction now reaches 16/16. This checks the supplied excerpt, not every exception or definition needed to interpret it.
- All retained excerpts in the latest run match the normalized source-page text. Source byte hashes and page counts are retained in the run manifest. Citation validity is distinct from value correctness and completeness.
- HTTP routes and selected actual browser flows pass; see RUNTIME_CHECKS.json and BROWSER_CHECKS.json. The three-page memo was rendered and all pages visually inspected.
- Financial tests independently confirm USD 2.6mm/bp portfolio DV01, USD 65mm PV versus USD 10mm annual coupon sensitivity for +25bp, credit/basis residuals and failure payoffs. These are first-order scenario identities, not independent derivative valuations.

## Source inspection scope

Re-read selected original PDF text: Bio-Techne pp. 2-3, 46, 71-72; Organon pp. 2-4, 60, 86-89; Uber pp. 2-4, 13, 15, 27, 34-35. Confirmed the material distinctions already recorded in CASE_REVIEW.md: vested/unvested award treatment, grant-year cohorts, no transaction financing condition versus lender conditions, automatic versus elective extension, Parent's remedy waiver, 12-month versus nine-month fee tails, exact price versus floor, financing floor versus bridge commitment, and separate regulatory clocks. These selected reads do not reconcile every operative clause, incorporated definition, omitted schedule or fee trigger.

## Required next steps

1. Limited live evaluation is complete; expand complete-clause evaluation beyond the two tested fields. Resolve the unsupported Uber financing-condition inference; preserve the candidate/history and require genuine human review before approval.
2. Expand semantic extraction and clause reconciliation for the unresolved critical fields. Do not promote a model proposal merely because its citation matches.
3. Rohit must inspect material source interpretations, calculations, assumptions and retained code, then record genuine approve/correct/reject decisions in the exported packet. It contains no pre-approved decisions.
4. Regenerate reports and the package after any model or review run. A review packet is tied to its base run and becomes stale after a new run. The package is prepared for review, not sent or submitted.
