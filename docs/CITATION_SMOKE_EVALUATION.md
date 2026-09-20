# Citation smoke evaluation: v6

Run `20260920T223116Z-7df8a279` used GPT-4.1 mini snapshot `2025-04-14` for five remedy-limitation requests. Four proposals were retained. No quotation-copying or unknown-passage-ID failures occurred. Bio-Techne's summary response failed because `normalized_value_json` contained invalid JSON. On the same five-request remedy subset, v5 retained two proposals and rejected three quotations. This small operational comparison is not a semantic accuracy estimate.

Usage: 18,003 input and 1,925 output tokens, for an estimated uncached $0.0102812 at the recorded prices. Cumulative reservations are $4.818261, leaving $5.181739. Reservations include the historical buffer and are not billed spend. No paid calls were made by the assistant during evaluation.

## Agent source findings for the four retained proposals

All findings are agent-authored; no expert legal review, human verification or completeness attestation is claimed. Physical PDF pages are used.

| Source and record | Finding |
|---|---|
| Bio-Techne agreement p. 60, `6f118f893e1232e34dc9eec2` | Captures several remedy limitations, but the value overstates a limitation on what Parent can be required to accept as a bar on imposition. It also omits the material-adverse-effect measurement based on a person with the revenues and net income of Parent's Life Science business. The cited passage contains that qualification; the value does not preserve it. |
| Organon summary p. 3, `45f7a0806587bb0aec80f5e8` | Wrong field focus: primarily describes no-shop/fiduciary-out provisions and general efforts rather than the requested remedy/Substantial Detriment limitation. Source-ID selection does not prevent an irrelevant-but-genuine citation. |
| Organon agreement pp. 71–72, `2a9854f593f11953fba6403b` | Still overstates limits on required actions, omits the continued definition and exceptions, and incorrectly claims no definitions are truncated. Its citations end with “material adverse” before the continuation. Parent consent/compulsion provisions and the extension election require separate treatment. |
| Uber agreement p. 27, `bece34eaafaddcc392470cdb` | Now distinguishes “not required to offer or accept” from the separate restriction on Delivery Hero acting without Uber's consent. However, the materiality summary generalizes the specific Asset Acquirer Transaction adjustment into “considering the transaction”; this scope qualification must be preserved. Selected-clause improvement is not full-field verification. |

The four records remain unverified candidates. `data/assessments/citation_smoke.json` binds these findings to their record IDs and PDF hashes; an offline refresh attaches them without changing normalized values or review status.

## v7 implementation response

The remaining format failure comes from asking the model to put JSON inside a JSON string. V7 requests an actual typed `normalized_value`: a scalar/null, or a structured object with `summary` and a list of labelled text details. The adapter serializes that validated value internally for compatibility with existing extraction records. Model-generated nested JSON is no longer required. Source-passage IDs and the existing integrity checks are retained.

Seventy-seven offline tests pass, including quoted text, newlines, booleans, numbers, unknown IDs, unexpected structures and nonfinite-value rejection. V7 has not been evaluated live. The same five-call `run_citation_smoke.sh` can test the new value schema before expanding field coverage. Passing the schema will not resolve the semantic failures described above.
