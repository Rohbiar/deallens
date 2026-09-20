# Broader live extraction: agent findings for human review

Run `20260920T170013Z-4017a08d`, GPT-4.1 mini snapshot `2025-04-14`, prompt v4. Fifteen selected fields produced 76 completed responses: 31 retained proposals (27 non-null), 36 exact-citation rejections and nine empty abstentions. Another 59 field/layer slots had no retrieved support and were not called. Retention is not accuracy. All proposals remain unverified; human approvals are zero.

Reported usage: 259,179 input and 40,443 output tokens. At the ledger's recorded prices, the uncached estimate is $0.1683804, not an invoice. Persistent reservations are $3.936138 including the $1 historical buffer, leaving $6.063862. No further paid calls were made during this evaluation.

## Priority review findings

These are agent recommendations, not applied decisions or an exhaustive legal review. Page numbers refer to physical pages in the original PDFs. To correct a field, inspect all its records and referenced definitions before attesting completeness. Rejection can be limited to a selected record. The exported packet `outputs/review_packet_20260920_broad.json` has no decisions or human attestation.

| Source / record | Finding and recommended review | Original pages |
|---|---|---|
| Organon fee triggers `b856de56f3a5c7e19b728e99` | Reject or correct the six-year fee tail. The defined Tail Period is used for D&O insurance; it is not the subsequent-acquisition fee tail. Reconstruct each termination trigger and the nine-month clause separately. | 28, 77, 87–89 |
| Uber borrowing conditions `051e0685adff1525204cc69a` | Reject: the proposal summarizes Defaulting Lender status, not conditions to initial borrowing. Review the actual operative conditions and exceptions. | 56 versus 89–90 |
| Uber remedy limits `cc84954c78d3bf22f2087119` | Correct or reject: absence of a duty to offer/accept certain remedies does not prohibit voluntary acceptance. Preserve the exact business scope and separate company consent restrictions. | 27, clauses 4.5–4.6 |
| Organon remedy limits `de51b900f1e5e4f1cddb79ee` | Correct or reject: the quoted clause limits what may be required; the proposal turns it into a prohibition. The definition continues on the next page and must be considered with Parent's extension election. | 71–72, 86–87 |
| Bio-Techne guarantee `0406568e0afc58eb215b497c` | Reject: an interim indebtedness covenant permitting certain guarantees does not identify an acquisition guarantor. | 49 |
| Uber guarantors `2458611d47d9f4073ea614c2` | Reject or narrow the empty list to the bridge's lack of subsidiary guarantees. It cannot negate the acquisition funding guarantee by Uber in the separate instrument. | 4, 15 |
| Bio-Techne vested options `4657e955eebea0f6617463b8`; Organon vested options `7d009e4cc5c2476dbab5f7d6` | Re-extract treatment. Missing quantities are not a reason to ignore disclosed conversion/vesting provisions. Do not approve a complete award field from this null proposal. | Bio-Techne 2, 16; Organon 38 and award provisions |
| Bio-Techne parent `d9e2ad36044faf39d5d3155e`; Organon parent `393252fe32cc067527c59443` | Unresolved aliases are not legal identities. Read agreement introductions and resolve Parent and acquisition vehicle separately before approving. | Bio-Techne 10, 44; Organon 13, 96 |

Other retained proposals remain open, including cross-referenced fee triggers, extension conditions, award cohorts and funding scope. No percentage of semantically correct proposals is asserted. The exact citations of retained records pass provenance checks, but the findings above demonstrate that provenance does not establish meaning.

## Engineering response and remaining work

Prompt v5 adds field-specific contracts for identities, guarantee scope, award treatment, fee tails, remedy modality, approvals and borrowing conditions. Retrieval prioritizes an operative borrowing heading; an offline check now includes Uber pages 89–90 within the bounded context. This does not establish retrieval completeness. New diagnostics distinguish unknown chunk IDs, short excerpts, nonexact excerpts and ambiguous excerpts while retaining strict exact matching. Historical rejected outputs cannot be diagnosed more precisely because their raw payloads were not retained.

The 66 unit/control tests and 16 selected scalar fixtures pass. These checks validate controls and selected baseline values, not the semantic effectiveness of v5. No live v5 results exist yet. Do not repeat the full batch unchanged. The next paid experiment should target the failure fields and compare retained semantics, citation rejection rates and required-context retrieval before broadening. Human review and the original assignment's complete legal extraction remain outstanding.
