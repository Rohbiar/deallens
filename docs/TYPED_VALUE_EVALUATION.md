# V7 typed-value smoke evaluation

Run `20260920T223823Z-cb902b0a`: five completed remedy-limitation responses, five retained candidates, zero citation failures and zero value-format failures. Both `source-passage-ids-v1` and `typed-values-v1` were exercised live. This is narrow format/provenance validation, not semantic accuracy or expert review.

Usage was 18,453 input and 2,695 output tokens: estimated uncached cost $0.0116932 at the recorded prices. The persistent guard has reserved $5.012576 including the historical buffer, leaving $4.987424. No new paid calls were made by the assistant.

## Agent source findings

| Record | Finding |
|---|---|
| Bio-Techne summary `10af8c922a6f0cc62c4546da`, p. 3 | Focuses on termination rights, fees and general covenants instead of extracting the regulatory remedy limitation. A mention of Burdensome Conditions does not make the broader summary a complete answer. |
| Bio-Techne agreement `123c074d8e362a629292366b`, p. 60 | Again states that remedies cannot impose burdens, where the source limits what Parent/Merger Sub can be required to accept. The Life Science revenues/net-income measurement is not preserved precisely. |
| Organon summary `53ae4745e13e0ea9f90fe84f`, p. 3 | Describes no-shop and fiduciary-out provisions rather than the Substantial Detriment/remedy limitation. Wrong field focus. |
| Organon agreement `9e5f7150973ac967e63ae329`, pp. 71–72 and 87 | Now captures Parent consent, compulsion and the extension-election consequences, but still overstates the materiality limit as a prohibition and omits the precise definition. This is increased detail, not complete or correct legal extraction. |
| Uber agreement `bf3e29386fa3487ab6274b03`, p. 27 | Regresses from the earlier no-duty distinction to “No acceptance” and “only accepting” language. Also generalizes the Asset Acquirer Transaction adjustment and omits the separate Delivery Hero consent/compulsion provisions. |

All five remain unverified candidates with null normalized values. Findings are bound to record/PDF identity in `data/assessments/typed_value_smoke.json`. Automatic `quality_flags` now highlight possible wrong-field focus and prohibited-versus-not-required language, but are heuristic warnings, not findings of legal error or approvals. The existing downstream gate continues to exclude all model candidates from supported answers and analytics.

## Decision

The transport/format smoke test is complete. Do not spend more budget repeating the same test. Further work should address complete-clause boundaries, controlling definitions, field relevance and assertion-level meaning before a broader extraction evaluation. The current model/prompt configuration is not reliable enough to approve these remedy interpretations.

Seventy-nine unit/control tests and 25 selected source fixtures pass. Full contract-wide semantic accuracy remains unmeasured, and the original assignment's complete complex-clause extraction and QA coverage remain unfinished. The review package is an auditable prototype, not a claim that every requirement is complete.
