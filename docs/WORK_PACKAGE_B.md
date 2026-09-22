# Work Package B: structured interpretation

## Outcome and scope

Milestones B1 through B4 are implemented as a bounded deterministic candidate
pass. `deallens.structured_terms.INTERPRETED_FIELDS` exports the five supported
fields and `interpret_term(field_name, context_bundle)` consumes Package A's
`retrieval-context/v1` bundle without creating a second evidence path.

All source interpretations remain `candidate` and `unreviewed`. A context with
no recognized operative statement is retained as a structurally valid
`unresolved` term with an empty statement list and a material
`no_recognized_atomic_statement` item. Neither outcome is self-promoted.
Package A dependency gaps and budgets remain attached and block machine support.
No provider call, paid API use, historical-run mutation, review decision, upload
or commit was made in this package.

## Schema and validation contract

`structured-terms/v1` represents each legal statement atomically. It separates
actor and role, modality/action/object, beneficiary, trigger, conditions,
exceptions, business scope, monetary amount and qualifier, time unit and anchor,
statement source IDs, and unresolved dependencies. Records bind to the source
PDF hash and Package A section/source IDs.

The fail-closed validator checks JSON safety, schema and source hashes, source
IDs, field-specific actor/modality/action relationships, timing and amount
shapes, duplicate statements, contradictions and independently supplied atomic
assertions. Remedy statements require an express scope, limit and exception.
Award statements require award type and cohort. Financing statements require an
explicit condition type and distinguish transaction-closing conditions, lender
funding conditions and Certain Funds restrictions. Empty statements are valid
only for a materially unresolved term. Shape and citation validation alone can
never establish semantic support.

## Milestones and measured source output

- B1 — versioned schema and mutation-resistant validator: complete.
- B2 — extension conditions and fee triggers/tails: complete as candidates.
- B3 — remedy limitations: complete as candidates for all three agreements.
- B4 — award cohorts and financing conditions: complete where disclosed by the
  shared source path. No absent financing context is fabricated.

The ordinary `ingest -> provision_records -> interpret_term` path currently
produces 14 structured terms and 34 atomic statements:

| Family | Bio-Techne | Organon | Uber / Delivery Hero | Total statements |
|---|---:|---:|---:|---:|
| Extensions | 3 | 1 | 1 | 5 |
| Fees/tails | 7 | 5 | 2 | 14 |
| Remedy limits | 1 | 1 | 1 | 3 |
| Award cohorts | 3 | 4 | 1 | 8 |
| Financing conditions | no source record | 1 | 3 | 4 |

This is a count of deterministic candidate statements, not supported-answer
coverage or a precision/recall result.

## B3 remedy limitations

The remedy grammar preserves three materially different structures:

- a prohibited requirement beyond a defined Burdensome Condition, including the
  protected parties and affected business scope;
- a required joint Remedial Action covenant subject to a Substantial Detriment
  limit, plus the target-side consent and Parent-compulsion exceptions; and
- a required best-efforts remedy covenant triggered by a competent authority's
  clearance position, bounded by adverse-and-material and completion-condition
  exceptions.

The key operative text was checked on physical PDF page 60 (Bio-Techne), pages
71–72 (Organon), and page 27 (Uber / Delivery Hero). The complete selected root
sections span additional continuation pages and retain 27, 21 and 8 conservative
Package A unresolved dependency diagnostics, respectively.

## B4 award cohorts and financing conditions

Award output preserves performance-period cohorts and target versus maximum
measurement for Bio-Techne (key physical pages 16–19), and the pre-2026 versus
2026-or-later RSU/PSU cohorts for Organon (pages 36–37). The Organon omitted
Disclosure Schedule is retained as a material statement-level unresolved item
where it qualifies the pre-2026 PSU treatment. The Uber award statement
preserves the named actor, reasonable-best-efforts modality, legal-permissibility
condition, actual-versus-target performance rule, beneficiary-consent exception
and unresolved ultimate outcome from pages 24–25.

Financing output distinguishes Organon's transaction-level statement that
financing availability is not a Closing condition (physical page 83) from the
bridge agreement's lender conditions for initial and post-closing borrowing and
its Certain Funds restriction (pages 89–90). It does not infer that satisfying a
lender funding condition satisfies the transaction Closing conditions.

## Verification

Targeted command:

```bash
.venv/bin/python -m unittest tests.test_structured_terms -v
```

Result on 2026-09-21: 24/24 tests passed. The six new B3/B4 source-backed tests
cover all three remedy clauses, award clauses across all three sources, and
Organon/Uber financing conditions. Mutations remove or change remedy actors,
scope and exceptions; award cohorts; lender roles and lender conditions. A
separate regression proves that no-match interpretations remain valid unresolved
records instead of being dropped or crashing bundle generation. Existing actor,
payee, exception, time-unit and contradictory-modality mutations continue to
pass.

Production grammar contains no transaction names, transaction-specific section
numbers, dates, amounts or frozen semantic-reference answers. Every emitted
statement uses source IDs from its supplied bundle. Passing these selected tests
does not measure contract-wide legal precision or recall.

## Coordinator integration and remaining limitations

The coordinator can persist every available field in `INTERPRETED_FIELDS` by
calling `interpret_term(field_name, record["context_bundle"])` and then
`validate_term(term, record["context_bundle"])`. Consumers must retain candidate
and unresolved records but must not use them as supported answers or analytics
facts. The D adapter owns translation from the generic statement schema to its
frozen canonical vocabulary; B intentionally exposes no transaction-specific
canonical payload.

Omitted schedules and incorporated documents remain unresolved. Clause grammar
cannot prove it recognized every exception, cohort or financing condition.
Conservative Package A reference diagnostics keep all current source terms
ineligible for machine support, and no independent atomic reference basis has
been attached to promote them. Human legal verification remains unavailable.
No workstream timer was maintained, so no retrospective time-saved estimate is
asserted.
