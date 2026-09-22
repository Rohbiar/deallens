# Work Package D: independent semantic challenge set

## Outcome and independence

Work Package D freezes `tests/semantic_reference.json` as a bounded, agent-curated challenge set before inspection of any new Work Package B output. It is not human gold, legal advice, or a contract-wide accuracy estimate. No paid model call or external upload was made. Existing extraction code, scalar fixtures, source PDFs, historical runs, and review records were not changed.

The frozen set contains exactly 16 cases:

- 12 source-backed supported cases: one case for each combination of three transactions and four priority families (extension conditions, fee triggers/tails, remedy limitations, and award cohorts).
- 4 deliberately unresolved cases: an omitted Bio-Techne regulatory-jurisdiction schedule, an omitted Organon PSU schedule exception, an ambiguous Uber award outcome governed by beneficiary consent and underlying award terms, and redacted Uber bridge-fee amounts.
- 72 supported atomic assertions. Each supported case has at least one assertion for actor, obligation, trigger, exception, timing, and scope.

The 72 assertions are the complete and finite supported-assertion denominator for this reference-set version. The four unresolved cases are a separate denominator and never inflate precision or recall.

## Direct source review

The PDFs were inspected directly with PyMuPDF page-preserving text extraction. Key pages were also rendered and visually checked to confirm page boundaries, headings, qualifiers, redactions, and continuation layout.

| Source | Physical pages examined | Reference focus |
|---|---|---|
| Bio-Techne | 16-19, 57, 59-61, 70-76 | PSU conversion and performance qualifier; Burdensome Condition; automatic Outside Date extensions; company-fee tail; omitted approval schedule |
| Organon | 34-39, 71-74, 84-89 | pre-2026 versus 2026-or-later awards; Substantial Detriment and Parent election consequence; elective Outside Date extension; nine-month fee tail; omitted schedule exception |
| Uber / Delivery Hero | 4, 12-18, 20-35, 51, 57-60, 63, 77 | BaFin-bounded Long-Stop Date; award-settlement efforts; remedy limit; company and regulatory reverse fees; bridge-fee redactions |

Every fixture records the immutable PDF SHA-256, document layer, agreement section, physical page, and a whitespace-reproducible excerpt. `validate_reference(..., root)` recomputes each source hash and requires every excerpt to occur on the specified physical page. This establishes provenance for the bounded assertions, not correctness beyond the inspected scope.

## Important semantic distinctions captured

- Bio-Techne extensions are automatic when the stated residual regulatory conditions remain; Organon's extension is elective by either Parent or Company through timely written notice; Uber's later regulatory date depends on BaFin authorization and cannot pass May 10, 2028.
- Bio-Techne's selected company-fee tail is 12 months; Organon's is nine months. Uber's selected reverse regulatory fee is a five-Business-Day payment deadline, not a subsequent-transaction tail.
- Remedy actors and limits differ. The Bio-Techne limitation protects Parent, Merger Sub, and affiliates from a defined Burdensome Condition. Organon's Parent election to extend changes the remedy covenant and waives a condition. Uber requires Acquiror best efforts only up to its adverse-and-material and closing-condition limits.
- Bio-Techne PSUs use maximum performance for incomplete performance periods. Organon divides RSU/PSU treatment at calendar-year 2026. Uber states elections and reasonable-best-efforts obligations; it does not establish one guaranteed uniform award outcome.

## Evaluator contract

`tests/evaluate_semantics.py` is intentionally independent of DealLens extraction modules. An integration adapter must emit canonical predictions:

```json
{
  "schema_version": "1.0",
  "cases": [
    {
      "case_id": "organon_outside_date_extension",
      "status": "supported",
      "assertions": [
        {"assertion_id": "organon_extension_obligation", "value": "elective_by_written_notice"}
      ]
    },
    {
      "case_id": "uber_bridge_fee_amounts_redacted",
      "status": "unresolved",
      "assertions": []
    }
  ]
}
```

Matching is exact JSON equality by `case_id` and `assertion_id`; the adapter owns mapping implementation-specific structured terms to this canonical vocabulary. A supported reference assertion receives exactly one mutually exclusive outcome:

- `correct`: asserted and equal;
- `incorrect`: asserted but unequal, including a wrong actor, flipped modality, wrong period, or dropped qualifier;
- `omission`: case or assertion absent;
- `abstention`: the implementation explicitly abstained on the supported case; or
- `unresolved`: the implementation marked a supported case unresolved.

Reference cases expected to remain unresolved are counted separately as `respected`, `incorrectly_resolved`, `omission`, or `abstention`. Out-of-scope predicted case IDs are disclosed but excluded from bounded metrics.

`bounded_atomic_precision = correct / (correct + incorrect)` uses only assertions actually made. `bounded_atomic_recall = correct / 72` uses the frozen supported-assertion denominator. Both metrics apply only to this reference set. A null precision is reported when no supported assertion is made.

## Final adapter

`deallens.semantic_predictions.build_semantic_predictions(terms,
case_descriptors)` is the only bridge from `structured-terms/v1` to the
prediction envelope. Case descriptors remain outside production logic and
contain selectors and source paths, never expected values. The adapter does not
import this reference set or encode transaction names, dates, amounts, section
numbers, or answers.

The adapter is deliberately fail-closed:

- `candidate` and `unresolved` terms produce an `unresolved` case;
- any term- or statement-level unresolved item whose materiality is `material`
  or `unknown` produces an `unresolved` case;
- ambiguous term or statement selection and missing mapped values produce an
  `unresolved` case;
- no matching term produces an explicit `abstention`; and
- only clean `machine_supported` or `human_verified` terms can emit assertions.

This permits B's final unpromoted output to be evaluated without pretending
that schema validity, clause retrieval, or agent interpretation establishes
semantic support. Generic identity, condition-text and party-name transforms
are available for future eligible records. Any vocabulary alignment remains
visible in caller-supplied descriptors.

## Tests and measured result

Targeted command:

```bash
.venv/bin/python -m unittest tests.test_semantic_predictions tests.test_semantic_evaluator -v
```

Result on 2026-09-21: 22/22 tests passed.
The nine evaluator tests validate source hashes and page excerpts, the explicit
72-assertion denominator, perfect bounded accounting, and seeded failures for
wrong actor, flipped modality, wrong nine-month tail, missing performance
qualifier, unsafe resolution of a redacted value, omission, abstention, and
unresolved status. Eleven adapter tests cover absence of transaction answers in
production code, transparent mappings, actor and timing mutations, candidate
and unresolved terms, term- and statement-level
material uncertainty, unknown materiality, ambiguous selection, absent terms,
missing paths, empty mappings and duplicate identifiers.

Two builder tests additionally validate the 16-case external descriptor catalog,
verify that it contains no `expected` values, and execute the command-line
builder against a synthetic persisted run.

These passing tests establish evaluator behavior and fixture reproducibility. They do not establish that current or future DealLens outputs are semantically accurate.

## First integrated bounded result

The final B interpreter was run deterministically over the Package A provision
records for D's four priority families in all three supplied PDFs. This produced
12 structured terms and 30 statements. All 12 terms remained `candidate`, all
retained unresolved context, and none was promoted for the evaluation.

The external descriptors used only the reference case ID, transaction, family,
assertion ID/dimension, generic statement kind, and generic structured path.
They did not contain expected values. Predictions and the diagnostic evaluator
report were written under `/tmp`, not into a current or historical run.

Exact bounded outcome:

| Category | Count |
|---|---:|
| Frozen supported assertions | 72 |
| Correct | 0 |
| Incorrect | 0 |
| Omission | 0 |
| Abstention | 0 |
| Unresolved | 72 |
| Asserted prediction denominator | 0 |
| Bounded atomic precision | null |
| Bounded atomic recall | 0.0 |

For the separate four-case unresolved-reference denominator, all four
limitations were respected. There were zero abstentions, incorrectly resolved,
or omitted unresolved-reference cases. Across all 16 cases, the adapter emitted
16 `unresolved` and zero `abstention` or `supported` predictions; it emitted no
out-of-scope case IDs.

This is the intended safe result for unreviewed candidates, not evidence that
the extracted interpretations are wrong. It establishes neither semantic
precision nor contract-wide recall. It shows that the implementation does not
silently turn candidate parsing into benchmark-supported assertions. Future
qualified validation can promote individual terms and expose their mapped
values to this unchanged frozen evaluator.

## Integrated-evaluation procedure

1. Keep `tests/semantic_reference.json` unchanged for the first integrated evaluation. If a source-reading correction is necessary, version the reference set and disclose the original and the reason; do not edit expectations to make output pass.
2. Supply external case descriptors to the D-owned adapter. Do not import B's implementation into the evaluator or duplicate transaction answers in production code.
3. Run `PYTHONPATH=. .venv/bin/python tests/evaluate_semantics.py PATH_TO_PREDICTIONS.json --output PATH_TO_REPORT.json`. The default command exits nonzero on incorrect assertions, omissions, abstentions on supported cases, unresolved supported cases, or unsafe/missing unresolved cases. `--no-fail` is available only when a diagnostic report is desired without a gate.
4. Report the five supported-assertion categories and the four unresolved-reference categories separately. Do not collapse abstentions or unresolved source limitations into correctness.
5. Have the coordinator own shared runtime wiring and final generated report. Work Package D does not modify current extraction code or historical generated outputs.

The reproducible persisted-run commands are:

```bash
PYTHONPATH=. .venv/bin/python tests/build_semantic_predictions.py \
  outputs/RUN_ID --output /tmp/deallens-semantic-predictions.json
PYTHONPATH=. .venv/bin/python tests/evaluate_semantics.py \
  /tmp/deallens-semantic-predictions.json \
  --output /tmp/deallens-semantic-report.json --no-fail
```

The builder also accepts the `outputs` directory or project root and resolves
its validated `latest.json` pointer. `--no-fail` is required for this diagnostic
candidate baseline because unresolved supported cases intentionally do not pass
the semantic completion gate. Omit it when testing a proposed fully supported
release gate.

## Remaining limitations

The set is deliberately small and was curated by the same class of agent participating in development, though it was frozen independently before new B output. It does not cover every provision, every referenced definition, every termination route, every award subtype, or the contents of omitted schedules. Exact canonical equality is useful for mutation resistance but requires a transparent adapter and does not replace qualified legal review. Any later machine review must be labeled as machine assessment and preserve disagreements rather than silently revising this set.
