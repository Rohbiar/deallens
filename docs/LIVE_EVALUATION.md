Latest update: see [BROAD_BATCH_REVIEW.md](BROAD_BATCH_REVIEW.md) for the 15-field live run, substantive failures, budget and offline-only v5 changes. Earlier results below are historical where they refer to two fields.

# Latest live evaluation: prompt v4

Run: `20260920T163210Z-a5687251`, 2026-09-20. Requested model `gpt-4.1-mini`; returned snapshot `gpt-4.1-mini-2025-04-14`. Same two fields (consideration per share and transaction financing condition); six-call cap per document. No budget exhaustion occurred.

| Document | Completed API responses | Retained proposals | Citation rejections | Empty abstentions |
|---|---:|---:|---:|---:|
| Bio-Techne | 4 | 2 | 1 | 1 |
| Organon | 3 | 1 | 2 | 0 |
| Uber / Delivery Hero | 5 | 4 | 0 | 1 |
| Total | 12 | 7 | 3 | 2 |

Six additional field/layer slots had no retrieved evidence and generated no API call. Provider-reported usage: 38,367 input tokens and 2,780 output tokens (41,147 total). Dollar cost is not reconciled against billing. The three rejections failed exact, unambiguous citation matching within the named retrieved chunk; no citation check was relaxed.

Of seven retained proposals, six contain non-null values and one is unresolved null. Agent inspection finds four price proposals and Bio-Techne's explicit absence of a transaction financing condition consistent with their selected cited sources. This is five limited source-consistency observations, not independently reviewed accuracy. Bio-Techne's financing value is now a boolean; the v3 type mismatch is resolved in this run.

**Material semantic failure:** Uber agreement p. 15 proposes `financing_condition=true` by citing clause 1.5. That clause describes a financing guarantee and funding obligations; the excerpt does not establish a transaction condition allowing the bidder not to complete if financing is unavailable. The proposal's 0.95 self-score and exact quote do not make this inference reliable. It remains an unverified candidate with null normalized value, excluded from supported QA and analytics. This agent assessment is separate in `LIVE_PROPOSAL_ASSESSMENT.json`; no human review event was manufactured and the immutable run was not edited. Do not flip the value to false without full clause review.

Uber's null summary candidate comes from forward-looking risk language and supplies no answer. The financing-exhibit request abstained, appropriately avoiding automatic equivalence between lender borrowing conditions and transaction financing conditions. Its substantive legal completeness is still unmeasured.

Compared with v3, invalid outputs fell from six of eleven responses to three of twelve. The samples are tiny, the budget changed and generation is stochastic: this does not prove a general quality improvement. Machine-supported field coverage remains 9/42, 8/42 and 11/42. Full semantic precision/recall remain null; human-verified records remain zero. The model added no approved facts.

Current verification: 59 tests and 16 selected scalar fixtures pass. The memo and review archive are refreshed to include this evidence. Broad semantic extraction, independent review and remaining assignment gaps are still outstanding. No further connectivity test is needed; prioritize complete clause evaluation over repeating these two fields.

---

# Historical first completed live model evaluation

Run: `20260920T162331Z-957420e8` (2026-09-20). Requested model: `gpt-4.1-mini`; returned snapshot: `gpt-4.1-mini-2025-04-14`. Prompt: `clause-extraction-v3`. Scope: consideration per share and transaction financing condition, across the same three source PDFs, maximum four logical calls per document. The preceding TLS-failed run is preserved separately.

## Measured outcomes

| Document | Completed API responses | Retained proposals | Invalid output |
|---|---:|---:|---:|
| Bio-Techne | 4 | 3 | 1 |
| Organon | 3 | 1 | 2 |
| Uber / Delivery Hero | 4 | 1 | 3 |
| Total | 11 | 5 | 6 |

Six field/layer slots had no retrieved support and were not requested. One Uber financing-agreement slot was skipped because the four-call budget was exhausted. Provider-reported usage totals: 31,894 input tokens, 3,404 output tokens, 35,298 total tokens. Dollar cost has not been reconciled against billing. All 11 responses completed on the first transport attempt; no successful live extraction is claimed for the earlier TLS-failed run.

## Agent assessment of retained proposals

- Bio-Techne summary p. 2 and agreement p. 12 each propose USD 73.00, exact, consistent with the scalar baseline and their cited source excerpts.
- Organon agreement p. 25 proposes USD 14.00, exact, consistent with the definition and baseline.
- Uber agreement p. 15 proposes at least EUR 41.50, preserving the floor qualifier. The summary/agreement qualifier difference remains unresolved; no canonical price is approved.
- Bio-Techne agreement p. 46 proposes a narrative describing sufficient funds and the explicit absence of a financing condition. The narrative broadly follows the cited provision, but its object value is incompatible with the boolean field expected by the review workflow. It must not be counted as a successful typed boolean extraction. The original candidate is retained unmodified in its immutable run.

Two rejected responses failed JSON decoding inside the encoded normalized value. Four had generic ValueError failures. The old audit did not retain specific validation reasons or rejected payloads, so their exact causes cannot be reconstructed reliably; do not label all four as citation failures. No validation checks were relaxed to improve apparent success rates.

This is a limited live integration evaluation, not complete legal extraction. Five retained responses out of eleven is an operational retention count, not semantic accuracy. The four price proposals agree with selected evidence; they do not establish award, fee, deadline, party-role or full-contract completeness. Human-verified records remain zero. All proposals remain candidate values with null normalized values.

## Changes after observing this run

Prompt v4 adds field-specific value contracts, explicit JSON boolean/null examples and focused contiguous citation instructions. Local validation now rejects narrative objects for the financing-condition boolean field and malformed monetary/calendar scalar types. Future invalid-output audits record safe diagnostic reasons. Skips after a provider failure are distinguished from genuine budget exhaustion. These changes pass 59 unit/control tests but have not yet been evaluated live. The v3 run is not relabeled as v4.

A repeat of these two fields with a six-call cap per document will allow all three layers to be attempted when retrieved evidence exists, including the previously budget-skipped Uber financing exhibit. Further evaluation must reconcile transaction financing conditions with lender borrowing conditions. Broader semantic extraction and real human review remain outstanding.

The earlier ZIP and technical memo predate this live run and should be refreshed after the follow-up evaluation. The current run, its model audit, this report and MODEL_EVALUATION.json are the authoritative evidence for this limited test.
