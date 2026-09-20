# Focused retest: v5 did not establish improvement

Live run `20260920T203028Z-779ed393` used GPT-4.1 mini snapshot `2025-04-14`, prompt v5 and four fields across all three sources. Eighteen completed responses yielded six candidates, ten nonexact-quotation rejections, one invalid nested JSON value and one empty abstention. On the same four-field request subset, v4 retained nine candidates with eight rejections and one abstention. These are paired operational counts, not semantic accuracy, and no statistical improvement is established.

Reported usage is 59,262 input plus 16,259 output tokens. At the ledger's recorded uncached prices, estimated usage cost is $0.0497192; actual billing and caching adjustments are not claimed. Cumulative reservations are $4.626291 including the historical $1 buffer, leaving $5.373709. The assistant made no paid calls during this analysis.

## Agent assessment of all six retained candidates

These are source-based agent findings, not expert legal review, approvals or automatic corrections. Physical PDF pages are listed below.

| Candidate | Assessment |
|---|---|
| Bio-Techne vested options, `4400665349aafda4d03f7a57`, summary p. 2 | The cancellation and cash intrinsic-value formula follow the cited paragraph; this fixes the earlier quantity-focused abstention. The Effective Time concerns cancellation/conversion and entitlement, so it must not automatically be interpreted as the actual cash payment deadline. No full award-field completeness finding is made. |
| Organon remedies, `3e83c1b7eef17ddfeb2275b6`, summary p. 3 | The detailed value says acceptance is prohibited. The cited summary describes a regulatory closing condition; it does not establish that general prohibition. |
| Organon remedies, `fcb3d25772371ffb2135eb6d`, agreement p. 71 | Again changes limits on what may be required into actions that may not be taken. Its excerpt starts mid-word and ends mid-definition. The complete text on pp. 71–72 distinguishes required efforts, consent restrictions and Parent's ability to compel conditional actions; the extension election on pp. 86–87 must also be considered. |
| Organon borrowing conditions, `eac5543070f8c1357e430e48`, agreement pp. 59 and 79 | Summarizes financing representations and Parent's financing covenants as if they were lender conditions precedent. The detailed conditions in the referenced commitment letter are not established by those excerpts. Parent's contractual efforts must remain distinct from lender funding conditions. |
| Uber fee triggers, `baf671405614992b4d873c60`, summary p. 3 | Mislabels the ten-business-day completion window as a fee tail and the long-stop date as a payment deadline. The reverse-fee trigger's regulatory non-completion qualification must be preserved. The layer-specific Company alias also needs resolution. |
| Uber fee triggers, `7f9c3df5352c580a5b3cc703`, agreement p. 35 | EUR 200m and EUR 700m amounts and five-business-day payment language occur on p. 35. However, the EUR 200m trigger and termination actor are wrong: the operative triggers start on p. 34, clause 13.3. A payment deadline is not a subsequent-transaction fee tail. |

No candidate has been promoted to a supported fact or human-verified record. Historical results remain immutable. Annotations are stored in `data/assessments/focused_retest.json` and can be carried into a new offline refresh.

## Concrete next change: citation selection instead of quotation copying

Prompt v6 supplies a bounded catalogue of exact source passages. The model selects a citation ID from a request-specific enum; the provider adapter attaches the original source excerpt, which still passes the existing chunk/page integrity checks. Unknown IDs and model-supplied replacement quotes are rejected. The catalog hash, size and protocol version are recorded in provider metadata. All retrieved text is preserved in the planned five-call smoke test.

This removes the task of reproducing long quotations from the model. It does not establish that the selected passage entails the proposed interpretation. The structured schema uses supported enum/object features from the [official Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs); that documentation also distinguishes schema compliance from semantic correctness.

Seventy-six offline tests pass. No v6 live result exists yet. The new `run_citation_smoke.sh` performs five requests on remedy limits, with approximately $0.192 reserved if each succeeds on its first attempt ($0.576 at three attempts each), within the existing guard. Do not repeat the full batch until this protocol has been evaluated live and its retained meanings checked.
