# Work Package E — financial reconciliation and term-to-scenario mapping

## Outcome and scope

The second-wave audit preserves the assignment's synthetic Bio-Techne inputs,
the four existing strategy implementations and the disclosed Uber bridge grid.
It adds an explicit, reusable boundary between supported structured terms and
hypothetical scenario inputs. No contractual extraction rule, source file,
historical run, current-run output, assumptions file, CLI, package or API state
was changed.

The new `term-scenario-mapping/v1` adapter in `deallens/analytics.py` consumes
structured extension and financing-condition terms. It emits separate:

- contractual facts, with term, statement and source identifiers;
- hypothetical party elections;
- synthetic financing and market inputs;
- assumptions that conditions are satisfied and the transaction completes;
- dated scenario inputs or explicit blocked reasons.

Only `machine_supported` or `human_verified` terms without material unresolved
items may drive a date. Candidate, relative, malformed, missing and materially
unresolved dates remain visible but block both extension scenarios. A supported
conditional date produces a labeled condition-satisfaction assumption. A
supported permitted or conditional extension also produces a labeled election
assumption; it never says the election occurred. Supported lender conditions
and transaction-completion conditions remain distinct, and neither is converted
into a factual conclusion that financing is available.

`run_analytics` accepts structured terms through an optional fifth argument.
The existing four-argument call and legacy excerpt-date path remain compatible.
The coordinator must decide when current structured terms have passed Package
B/D validation and wire them into the CLI; Package E did not alter `cli.py`.

## Required scenario and sign audit

The three rate shocks, combined +25bp benchmark/+20bp issuer-credit shock and
two delay scenarios were already represented. Before this package, however,
the generic assignment requirement “Transaction failure” was satisfied only by
`failure_rates_down_25`, which coupled the legal outcome to a directional rate
forecast. The implementation now includes a neutral `failure` scenario at 0bp.
The existing `failure_rates_down_25` and `failure_rates_up_25` rows remain as
separate stress sensitivities. This makes the seven required scenarios explicit
without deleting useful additional cases. The expected-value illustration
continues to use its separately disclosed assumption of -25bp on failure; it is
not relabeled as the neutral requirement case.

The existing sign and unit conventions reconcile as follows:

- Portfolio DV01 is USD 4bn / USD 100mm × USD 65,000 = USD 2.6mm/bp.
- A +25bp benchmark shock is USD 65mm financing-cost PV. The annual coupon
  increment is USD 10mm; it is a different measure and is not added to PV.
- Bond financing cost uses benchmark plus issuer spread. The 15bp initial swap
  spread is not added again to the bond coupon.
- Positive hedge P&L is a receipt and positive net incremental cost is worse for
  the issuer. A payer swap offsets benchmark exposure, not issuer credit spread.
- A conventional forward hedge can create a failure unwind gain or loss. The
  synthetic deal-contingent swap has no failure settlement and retains only its
  assumed fee. The ordinary payer option retains its independent failure payoff.
- Commitment amounts and assumed drawn balances stay separate. Bridge interest
  is an annualized run rate; it is not a lifetime cashflow or a fixed-rate DV01.
- Transaction termination fees are not used to offset hedge breakage.

## Disclosed bridge mapping and redactions

`bridge-scenario-inputs/v1` in `deallens/financing.py` keeps the disclosed rating
grid as a contractual fact while requiring pricing-level selection, drawn
balance and benchmark rate as explicit assumptions. It calculates an annualized
interest run rate only when all three inputs are supplied. Disclosed redactions
(`margin_stepup_amount`, `duration_fee_amount`, and `funding_fee_amount` in the
tested fixture) are returned as `value: null`, `status: redacted`; a synthetic
step-up or fee cannot populate them.

## Verification and bounded coverage

Targeted command:

```bash
PYTHONPATH=.:tests .venv/bin/python -m unittest test_disclosed_financing test_term_scenario_mapping -v
```

Result: 11 tests passed. The new cases independently calculate 102 and 194 days
from the synthetic 2027-03-15 issue date to the two example extension dates,
USD 8mm as 20bp of USD 4bn, and USD 17.5mm as USD 500mm × (2.50% + 1.00%).
They also mutate support status, material unresolved state, missing timing,
funding-condition role, missing bridge assumptions and non-finite inputs.

Full regression command:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Result after concurrent Package B2 integration: 153 tests passed. Passing
Package E tests establish the specified synthetic identities and fail-closed
controls, not legal accuracy or independent derivative valuation.

Before this package, seven required scenario labels were counted only by mapping
transaction failure to a -25bp coupled stress, and structured B terms had no
analytics consumer. After it, neutral failure directly represents the seventh
requirement, directional failure stresses remain additional, and supported
structured dates can generate the two delay inputs with explicit assumption
lineage. This coverage statement concerns the synthetic scenario set only.

## Source scope and limitations

The audit re-read the relevant stored PDF pages without changing them:

- Bio-Techne physical pages 71–72: automatic extension language.
- Organon physical pages 86–87: elective extension and its Parent consequence.
- Uber / Delivery Hero physical page 13: BaFin-authorized later date and cap.
- Uber / Delivery Hero physical page 77: redacted duration-fee terms.

The mapping tests themselves are synthetic and do not assert that Package B has
completed structured interpretations for these pages. The adapter deliberately
blocks candidate terms. It does not value curves, volatility, convexity, hedge
accounting, early unwind or negotiated deal-contingent terms. Actual lender
conditions, rating selection, utilization, elections and completion remain
unknown unless separately supported or explicitly assumed.

## Integration steps

1. Package B should encode each usable calendar extension as a distinct
   statement with `timing.clock_type` of `absolute`, `fixed_date` or
   `calendar_date`, `timing.unit: date`, and an ISO `timing.value`. Conditions
   may remain on the statement or timing object.
2. For financing-condition statements, B/coordinator should use
   `business_scope.scenario_role` values `transaction_completion_condition`,
   `lender_funding_condition` or `funding_source`; unknown roles remain
   `unclassified_funding_fact` rather than being guessed.
3. After Package B/D validation, the coordinator should pass the applicable
   structured terms to `run_analytics(..., structured_terms=terms)` in `cli.py`
   and retain `term_scenario_mapping` in the output bundle.
4. Update the coordinator-owned requirement audit so neutral `failure`, not the
   directional failure stress, is the direct transaction-failure mapping. Keep
   the two directional failure rows disclosed as additional sensitivities.
5. No assumptions-file change is required for this package. If a future shared
   schema adds named scenario shocks, preserve the current values and their
   synthetic designation rather than deriving them from contract language.

No workstream timer was maintained, so no retrospective elapsed-time or agent
leverage estimate is asserted.
