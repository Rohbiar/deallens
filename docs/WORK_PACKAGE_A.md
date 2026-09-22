# Work Package A — retrieval dependency context

## Outcome and scope

The existing numbered-section pipeline in `deallens/provisions.py` now emits a
versioned, JSON-safe evidence graph for every source-provision record. It keeps
the existing full-section retrieval and QA fields, adds bounded recursive
same-instrument dependency expansion, and reports cycles, missing or ambiguous
targets, unrecognized reference syntax, omitted schedules and budget limits.
It does not interpret the clauses or label them globally complete.

No transaction names, source-specific section numbers, dates or amounts were
added to generic retrieval logic. No paid provider call was made. Historical
runs, source PDFs, review decisions and the API budget ledger were not changed.

## `retrieval-context/v1` contract

`build_context_bundle(doc, sections, selected_sections, *,
definition_terms=(), max_depth=3, max_chars=60000, max_nodes=64)` returns:

```text
schema_version       "retrieval-context/v1"
source_hash          full source-PDF SHA-256
document_id          source document identifier
root_section_ids     ordered selected section IDs
section_ids          ordered included section IDs
sections             [{section_id, document_layer, number, title, root,
                       source_ids, boundary}]
definitions          [{definition_id, document_layer, term, section_id,
                       source_ids}]
sources              exact page spans; each includes stable source_id and
                     section_id in addition to locator/page/offset/evidence
edges                [{kind, from_section_id, to_section_id, expression,
                       target, status, reason, source_ids}]
unresolved           [{kind, from_section_id, expression, target, reason,
                       details}]
budget               {max_depth, max_chars, max_nodes, used_chars,
                       used_nodes, truncated, exhausted_by}
recognition          {reference_expressions, recognized_targets,
                       unrecognized_expressions}
completeness         always "not_established"
```

Section IDs distinguish duplicate numbers by instrument and occurrence. Source
IDs derive from the source hash, immutable page locator/offset span and owning
section or definition, rather than an array position. A resolved reference or
definition edge names the exact supporting `source_ids`, so a consumer does not
need to guess which flattened span supports a statement.

Reference statuses are `resolved`, `missing`, `ambiguous`, `cycle`,
`budget_exhausted`, or `depth_limit`. Stable unresolved reasons include
`missing_target`, `ambiguous_target`, `instrument_boundary`, `cycle_detected`,
`depth_limit`, `character_budget`, `node_budget`, `unrecognized_reference`, and
`missing_definition`. Root sections are never silently truncated; if roots alone
exceed a configured limit, `root_exceeds_budget` is disclosed.

Multi-target expressions produce one edge per numbered target while retaining
the full source expression. For example, `Sections 5.01(a), (b), and 5.02`
produces targets `5.01` with subsections `a,b` and `5.02`. Partially understood
forms such as a section range remain in `unrecognized_expressions` even if an
endpoint was recognized. Schedule, annex and exhibit references are explicit
unresolved dependencies because the numbered-section index cannot establish
their availability or boundaries.

## Legacy adapter mapping

`provision_records` attaches the complete graph as `context_bundle` without
removing established record keys:

- `evidence_sources` remains the selected root-section spans.
- `reference_context` is a direct-root, one-hop view derived from graph edges;
  graph `resolved` maps to legacy `located`, and `budget_exhausted` maps to
  legacy `context_limit`.
- `definition_context` maps requested definition edges to the existing
  `{term, status, sources}` shape.
- `candidate_value.sections` remains the ordered root section numbers.
- `all_evidence` validates the bundle's complete flattened source set when a
  bundle is present.

This preserves the current QA/browser interface. `semantic.py` and
`citations.py` were deliberately not changed. The coordinator should make any
model-request adapter select the same `context_bundle.sources` (subject to an
explicit downstream budget) and retain `unresolved` plus `budget`, so displayed
evidence and model context cannot silently diverge.

## Verification

Targeted command:

```bash
.venv/bin/python -m unittest tests.test_retrieval_dependencies tests.test_provisions -v
```

Coverage comprises the 12 pre-existing provision tests plus 10 new dependency
and source tests. Mutations cover a recursive cycle, duplicate numbers across
instruments, duplicate headings within one instrument, a missing schedule,
multiple referenced subsections, a partially parsed range, character-budget
exhaustion, an unrecognized reference, stable definition evidence attribution,
JSON serialization and source-hash binding.

Full regression command:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

An integration checkpoint passed 115 tests. A final rerun after concurrent Work
Package D files appeared ran 116 tests but reported two class-setup errors because
its not-yet-created `tests/semantic_reference.json` was absent. No Work Package A
test failed. The Work Package A increment is the 10 passing tests in
`test_retrieval_dependencies.py`; the targeted 22-test A suite passes. Passing
engineering checks are not contract-wide semantic accuracy.

## Source pages examined and bounded coverage

The source-backed test ingests the pinned bytes of all three PDFs and checks the
following extension/fee continuation spans. Every attached root and dependency
span is revalidated against its normalized source page:

| Source | Extension continuation pages | Fee continuation pages |
|---|---:|---:|
| Bio-Techne | 71–73 | 71–76 |
| Organon | 86–87 | 87–90 |
| Uber / Delivery Hero | 12–14 | 34–35 |

Before this package, these root continuations were present but reference context
was one hop and did not expose a unified budget, stable graph IDs, cycle state or
unresolved dependency list. After it, all six tested document/field pairs retain
the same root continuations and expose recursive bounded context. This is a
targeted retention/dependency scope, not whole-contract recall or legal
precision. The prior selected provision fixture denominator remains separate.

## Remaining limitations and integration steps

- Numbered headings remain the entry point. Unnumbered clauses and external or
  incorporated documents may only appear as unrecognized/unresolved context.
- Same-instrument duplicate section numbers are intentionally ambiguous rather
  than guessed. Cross-instrument lookup is blocked and reported.
- Definition expansion begins from the field-specific generic term lists already
  used by provision retrieval. It cannot prove that every legally material
  defined term was recognized.
- Normalized page text and offsets remain the citation authority used by the
  existing application; exact citation establishes provenance, not correctness.
- Real bundles can legitimately exhaust the default character/depth budget.
  Consumers must retain those states and may not promote a bounded bundle to
  complete.

Coordinator integration is limited to reviewing the contract, wiring the
bundle into model-context selection in shared files, and rerunning the full
suite plus current source/provision evaluators. B and C can consume the graph
directly from each source-provision record. No migration of historical records
is required; consumers must tolerate records without `context_bundle`.

No workstream timer was maintained, so no retrospective elapsed-time or leverage
estimate is asserted.
