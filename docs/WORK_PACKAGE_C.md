# Work Package C — synthetic structured consumers

## Outcome and boundary

The second-wave consumer phase is implemented against synthetic
`structured-terms/v1` fixtures. QA, comparison, timeline, risk, and browser
rendering can now keep supported atomic components separate from unresolved
components without changing historical extraction records. Candidate or
unresolved terms do not become supported answers. Strict QA accepts only
`human_verified` structured terms, and the assignment's exact unsupported
sentence is unchanged.

This phase did not interpret the three source agreements, consume real B2
outputs, call a provider, refresh a generated run, or change a review decision.
No source pages were examined because the dispatched phase expressly uses
synthetic terms until Package B produces real structured outputs.

## Consumer interfaces

- `qa.answer(question, records, comparisons, strict=False,
  structured_terms=())` remains backward compatible. It adds
  `supported_components` and `unresolved_components`, blocks structured
  cross-layer conflicts, preserves legacy conflicts, and reports a partial
  answer whenever a required field or material component remains unresolved.
- `risk.risk_map(records, structured_terms=())` adds structured supported and
  unresolved components to each analytical risk link. A mixed result is
  `partial`, not supported.
- `term_comparison.compare_structured_terms(terms)` compares actors,
  modalities, actions, beneficiaries, triggers, conditions, exceptions,
  business scope, amounts, and timing. Different supported components are a
  conflict; any candidate or unresolved component forces `unresolved` and can
  never be a match.
- `term_timeline.structured_term_timeline(terms, strict=False)` retains the
  actor, modality, election state, conditions, exceptions, clock, and evidence
  IDs. Every projected event has `occurrence_status=not_established`; an
  elective or conditional extension is never represented as having occurred.
- The browser has optional rendering for `structured_comparisons`,
  `structured_timeline`, and the new QA/risk component lists. Source/model text,
  party names, actions, conditions, exceptions, scopes, IDs, and uncertainty
  reasons pass through the existing HTML escaper.

Machine-supported remains distinct from human-verified. The consumer trusts a
term's already-validated status; the coordinator must only persist a
`machine_supported` record after Package B validation succeeds.

## Verification and bounded coverage

`tests/test_structured_qa.py` uses only synthetic contexts and terms. Its ten
tests cover:

- Parent-versus-Company extension elections;
- actor-aware cross-layer conflicts and uncertainty that cannot match;
- timeline retention of actor, election, condition, and non-occurrence;
- a supported award cohort with an unresolved schedule/cohort;
- exact unsupported wording and strict-mode exclusion;
- conflicting legacy prices remaining blocked;
- separate risk-map supported and unresolved components;
- all 12 required question categories over three synthetic documents (36
  fail-closed answers); and
- escaping at the browser rendering boundary.

Targeted command:

```bash
.venv/bin/python -m unittest tests.test_structured_qa tests.test_core tests.test_provisions -v
```

Result during implementation: 45/45 tests passed. Passing synthetic consumer
tests do not establish semantic accuracy or improve the current source-backed
36-answer coverage. Before and after this isolated phase, the current generated
run remains 12 supported, 22 partial, one review-required, and one conflicted
answer; it was intentionally not regenerated.

The UI script also passed a JavaScript parse check, and the repository-wide
command `.venv/bin/python -m unittest discover -s tests -v` passed 139/139 tests
after the concurrent second-wave files were present. Run IDs printed by that
suite belong to temporary synthetic/offline integration fixtures, not a refresh
of the pinned current deal run.

## Exact coordinator integration steps

After Package B emits validated real terms, the coordinator-owned wiring should:

1. Persist or load a document's `structured_terms` beside legacy extraction
   records without rewriting historical records.
2. In `cli.py` bundle generation, add:
   `structured_comparisons = compare_structured_terms(structured_terms)` and
   `structured_timeline = structured_term_timeline(structured_terms)`, and call
   `risk_map(records, structured_terms)`.
3. When constructing the twelve QA answers and serving `/ask` in `cli.py` and
   `server.py`, pass `structured_terms=structured_terms` to `qa.answer`.
4. Keep the legacy comparison and timeline arrays intact for compatibility;
   expose the two structured arrays under their new names used by the browser.
5. Reject or retain as candidate any term that fails `validate_term`; never
   relabel it `machine_supported`. Preserve Package A unresolved dependencies
   on the term so these consumers display them.
6. Rerun the full suite, the frozen Package D semantic evaluation, and the 36
   current questions before refreshing reports or packaging.

No changes are required in `extract.py` for this phase. The coordinator may
later choose a storage representation and adapter after reviewing B2's actual
output shape.

## Remaining limitations

- No real structured term has yet passed through these consumers, so current
  run status and source-backed coverage are unchanged.
- Structured comparison is exact component comparison, not a legal-equivalence
  engine. Semantically equivalent paraphrases remain unresolved or conflicting
  unless normalized upstream.
- A missing summary or agreement structured term does not prove the term is
  absent. The comparison remains unresolved rather than inferring equivalence.
- The browser paths are present but remain dormant until coordinator-owned
  bundle/server wiring supplies the optional structured fields.
- Complete award cohorts, remedies, financing conditions, fee tails, omitted
  schedules, and redactions remain bounded by Package B interpretation and
  Package A context availability.

No workstream timer was maintained, so elapsed time and leverage are not
retrospectively asserted. No commit was created.
