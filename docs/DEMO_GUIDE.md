# DealLens demonstration and ownership guide

This guide supports a short technical walkthrough. Source assessments and the semantic reference set are agent-curated, not legal advice or human verification. Do not attest to review that has not occurred.

## Five-minute demonstration

1. Run `python -m deallens.cli serve` and open `http://127.0.0.1:8765`. Confirm run `20260922T024418Z-d989f939` and code commit `defe4a3` in the manifest.
2. In **Overview**, show the three source hashes, transaction classifications and separate supported, excerpt and structured-candidate counts. Bio-Techne's filing date must read PDF-metadata-reported; Organon and Uber are SEC-index-verified.
3. In **Evidence**, open a complex field. Show full numbered sections, stable source IDs and explicit unresolved dependency reasons. Explain that recursive context and exact citations establish provenance, not interpretation.
4. In **Ask DealLens**, ask Bio-Techne's consideration. Show the supported scalar and PDF source. Enable strict mode: the system abstains because no record is human-verified.
5. Ask Organon how the outside date may be extended. Expand its structured components to show the actor, election, written notice, conditions and unresolved context. The answer remains partial and does not claim an election occurred.
6. Ask Uber about awards or remedies. Show the bounded candidate statements and open consent, award-term or remedy dependencies. Then ask Uber consideration and show the exact-versus-at-least conflict.
7. In **Comparison**, **Timeline** and **Risk map**, show structured components and uncertainty. Confirm the timeline uses `not_established` occurrence state and source/model text is escaped.
8. In **Analytics**, select Bio-Techne's neutral `failure` scenario. Contrast it with `failure_rates_down_25` and explain the conventional swap's possible unwind loss, the option's separate payoff and the contingent swap's retained fee. Show extension scenarios as hypothetical, not completed elections.
9. End with the requirement and semantic reports. State that 179 tests, 25/25 source fixtures and 18/18 provision fixtures pass, while the bounded semantic result is zero asserted, null precision and zero recall; all four intentionally unresolved cases are respected.

## Calculations to explain

- USD 4bn contains forty USD 100mm units. Forty times USD 65,000/bp gives USD 2.6mm/bp. A +25bp shock is USD 65mm first-order PV cost and USD 10mm additional annual coupon cost; those measures are separate.
- The assumed debt coupon is 4.25% benchmark plus 1.00% issuer spread. The 4.40% swap rate implies a 15bp swap spread, which is not added again to the bond coupon.
- A payer swap offsets benchmark DV01 under the simplified assumptions but leaves credit and basis risk. Option premiums and contingent fees are synthetic inputs, not market quotes.
- The neutral failure scenario has a 0bp market shock. The expected-value illustration separately assumes -25bp on failure and says so.
- Uber's bridge grid is disclosed; draw, EURIBOR and rating selection are assumptions. Redacted fee and step-up amounts remain null.

## Reproduce the checks

```bash
python -m unittest discover -s tests -v
python tests/evaluate_sources.py
PYTHONPATH=. python tests/evaluate_provisions.py
PYTHONPATH=. python tests/build_semantic_predictions.py outputs/20260922T024418Z-d989f939 --output docs/SEMANTIC_PREDICTIONS.json
PYTHONPATH=. python tests/evaluate_semantics.py docs/SEMANTIC_PREDICTIONS.json --output docs/SEMANTIC_EVALUATION.json --no-fail
PYTHONPATH=. python tests/evaluate_requirements.py
PYTHONPATH=. python tests/check_runtime.py
```

## Accurate summary

“One reusable application processes all three sources. It preserves exact evidence and source distinctions, adds bounded structured candidates for complex clauses, and fails closed when dependencies or semantic support remain unresolved. Engineering and selected source checks pass. The current bounded semantic evaluation demonstrates conservative abstention, not semantic accuracy. No human legal verification or live hedge recommendation is claimed.”
