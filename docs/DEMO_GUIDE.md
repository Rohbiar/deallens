# DealLens demonstration and ownership guide

This guide helps explain the prototype without requiring you to certify legal interpretations. The source assessments were performed by Codex; they are not expert legal advice or human verification. You remain responsible for the submission and should be comfortable explaining the calculations, controls and limitations. Do not attest to review you have not performed.

## A five-minute demonstration

1. Run `python -m deallens.cli serve` and open `http://127.0.0.1:8765`. Restart an older server once to load updated Python code. After that, **Refresh run** loads the latest completed results. The footer identifies the run.
2. In **Overview**, show the original document, checksum, transaction classification and separate machine-supported/human-verified counts. Filing dates and external page completeness are explicitly unresolved.
3. In **Evidence**, search `parent_or_bidder`. The shared rules read legal names from each agreement's party introduction. They do not assume the company filing an 8-K is the acquisition target. Search `Agent source check` to find annotated model errors in a run carrying the broader batch.
4. In **Ask DealLens**, ask Bio-Techne's consideration per share. Show the answer and its PDF citation. Turn on **Require human-verified evidence** and repeat: the system abstains because no human has approved the record.
5. Select Uber and ask its consideration. The source comparison preserves the summary's EUR 41.50 and the agreement's **at least** EUR 41.50. It blocks a canonical answer. This is a qualification difference requiring reconciliation, not a claim that the documents necessarily contradict legally.
6. In **Analytics**, select Bio-Techne and `rates_up_25`. Explain USD 2.6mm/bp DV01 and USD 65mm incremental financing-cost PV. Compare unhedged, forward payer swap, payer option and the synthetic deal-contingent swap. Show a failure scenario and explain why the ordinary swap may require an unwind payment.
7. End with the current requirements audit. It distinguishes implemented controls from incomplete semantic coverage. Do not describe all 42 fields or all twelve questions as completely answered.

## Calculations you should be able to explain

- USD 4bn contains forty USD 100mm units. Forty times USD 65,000/bp gives USD 2.6mm/bp. A +25bp shock therefore implies USD 65mm first-order PV cost. The same rate change implies USD 10mm additional annual coupon cost; those two measures must not be added.
- The debt benchmark-plus-credit assumption is 4.25% + 1.00% = 5.25%. The separate 4.40% swap rate produces a 15bp swap spread. Adding that spread again to the debt coupon would double-count exposure.
- A payer swap offsets the assumed benchmark DV01, but leaves issuer-credit risk and introduces swap-spread/basis exposure. Its protection is conditional on the simplified model assumptions.
- Option premiums and contingent fees are explicit synthetic inputs. The ordinary option and synthetic deal-contingent swap have different failure payoffs. These are scenario illustrations, not market-valued hedge recommendations.
- Validation funding sizes, fee grids and some timing assumptions are synthetic. The EUR bridge commitment is neither proof of drawdown nor a seven-year fixed-rate bond exposure.

## Reproduce the checks

```bash
python -m unittest discover -s tests
python tests/evaluate_sources.py
PYTHONPATH=. python tests/evaluate_model.py
PYTHONPATH=. python tests/evaluate_requirements.py
PYTHONPATH=. python tests/check_runtime.py
```

`evaluate_model.py` reports retained historical API responses when the latest run is an offline refresh. It does not call a model. `python -m deallens.cli refresh` reruns common offline rules and retains historical candidates, annotations and request audits. It refuses changed PDFs or human-reviewed runs. A new live run uses the configured key and persistent budget guard.

## What can be said honestly

“One reusable application processes all three sources. It supports a limited set of explicit facts, preserves evidence and source differences, and fails closed on unresolved interpretations. We tested it against selected source fixtures and negative control cases. Live model testing exposed substantive errors; those findings are disclosed. Expert legal review and exhaustive semantic accuracy measurement have not occurred.”

No legal attestation is required to follow this guide. If a qualified reviewer later reviews complete fields, the separate review workflow can record those real decisions. Do not use it merely to make the verified count increase.
