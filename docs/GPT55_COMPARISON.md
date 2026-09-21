# GPT-5.5 comparison results

Run: `20260920T233813Z-64f21f5e`; baseline mini run: `20260920T223823Z-cb902b0a`.
Five requests used identical v7 retrieval passage hashes, typed values and source passage IDs. GPT-5.5-2026-04-23 used medium reasoning and one attempt per request. Four proposals were retained; Organon's agreement response failed local citation-count validation. This is a purposive comparison, not an accuracy benchmark or human review.

| Source | Agent assessment compared with mini |
|---|---|
| Bio-Techne summary, physical pages 2–3 | Better field focus: Burdensome Condition closing condition; missing definition explicitly acknowledged. |
| Bio-Techne agreement, pages 60 and 71 | Preserves not-required rather than prohibited, Life Science revenues/net-income measurement, closing conditionality and Parent control. |
| Organon summary, page 3 | Correctly focuses on Substantial Detriment, distinguishes closing condition and efforts covenant, acknowledges missing definition. |
| Organon agreement | Rejected: `A proposal requires bounded citations`. Actual citation count and response content were not retained; semantic quality cannot be assessed. |
| Uber/Delivery Hero agreement, page 27 | Details preserve obligation modality, Asset Acquirer Transaction adjustment, conditionality and consent/request duties. Summary compresses consent/request relationship using “unless”; use the separate source duties, not an inferred blanket consent exception. |

All four retained records remain unverified candidates with normalized_value=null. Agent annotations are in data/assessments/gpt55_comparison.json. They do not approve or promote any record. Source excerpts and uncertainty, not model self-confidence, inform the comparison.

Usage: 18,443 input tokens and 7,902 output tokens, including reasoning. At the recorded rates of $5/$30 per million input/output tokens, estimated usage cost is **$0.329275**, not independently reconciled billing. The local ledger reserved $3.030410 for this run and has $1.957014 remaining. User-reported prior account usage of $0.30 is distinct from this run's estimate. Reservations remain unchanged.

## Implementation correction and next run

The API schema omitted the local 1–12 citation limit and 20-proposal maximum. Both bounds are now present in the strict output schema. Prompt v8 states the limits and permits separately supported proposals when needed; it does not authorize dropping material qualifiers. Local validation remains in place. Array bounds are documented at https://developers.openai.com/api/docs/guides/structured-outputs . Automated validation: **81 tests pass**, including unchanged rejection of zero/13 citations and matching transport bounds. Live validation of this correction remains pending.

Run in the credential-bearing Terminal:

```bash
bash scripts/run_gpt55_organon_retest.sh
```

Two requests (Organon summary and agreement), with at most **$1.236980** conservative reservation; one attempt each. Do not rerun the full five-request comparison against the remaining allowance. The targeted run becomes the latest snapshot and contains Organon only; the complete three-document comparison stays preserved at the run path above. Final packaging must explicitly select/assemble the reviewed run lineage rather than treat this targeted snapshot as a complete assignment.

Next: inspect the retest, then decide which complex fields justify further model evaluation, resolve retrieval and interpretation gaps, complete the requirement audit, and regenerate final memo/package from explicitly selected runs. The current archived package predates this comparison and is not the final GPT-5.5 deliverable.

## Retest completed

Organon v8 retest `20260920T234423Z-9b827d83` retained both responses. See [GPT55_ORGANON_RETEST.md](GPT55_ORGANON_RETEST.md) for interpretation findings, remaining qualifier omission and usage. No further retest is currently requested; the command above is historical. Remaining local reservation allowance is $0.720034.

Current packaging update: three-document run 20260921T034805Z-88a4e5cf consolidates the comparison and retest with source-bound agent annotations and zero new provider calls. The updated three-page memo and hash-verified review archive now include these results and both parent-run folders. Earlier statements about a single-document latest snapshot or stale archive describe the state before this consolidation. Complex semantics and QA coverage remain partial.
