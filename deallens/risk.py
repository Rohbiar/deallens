"""Analytical links to evidence; these are review prompts, not legal opinions."""
RISKS={
 "benchmark_rate":("funding_sources","A planned fixed-rate debt issue becomes more expensive when its benchmark rises. Size the hedge against the financing exposure, not acquisition headline value."),
 "swap_spread":("interest_basis","A payer swap follows swap rates. For a benchmark-quoted bond, changing swap-minus-benchmark spread leaves basis risk."),
 "issuer_credit_spread":("financing_conditions","A rates hedge does not lock the issuer's credit spread or ensure access to bond markets."),
 "fx":("consideration_per_share","Compare consideration currency with actual cash and funding currencies. Same-currency funding can reduce transaction FX exposure; do not assume the whole acquisition is USD-funded."),
 "timing":("extension_dates_and_conditions","Distinguish automatic extensions from elections. A delayed close may require a hedge roll or option renewal; contractual long-stop is not expected issuance date."),
 "completion":("approval_or_tender_threshold","Specify which transaction outcome constitutes completion, including a tender threshold rather than automatically assuming a merger vote."),
 "regulatory_remedies":("remedy_limitations","Remedy limitations and election-dependent changes can alter completion risk. Read cross-references before defining deal-contingent exclusions."),
 "unwind_breakage":("fee_triggers_and_tails","A conventional payer hedge may create a payment on failure after rates fall. A transaction termination fee is not automatically received by the hedging entity or available to cover that payment."),
 "bridge_refinancing":("financing_maturity","Align bridge maturity, availability, benchmark resets, rating margins, duration fees and refinancing plans. Do not value a floating bridge with the seven-year fixed-debt DV01."),
 "award_cash_timing":("award_cohort_differences","Separate cash paid at closing from continuing service-based awards when estimating actual funding needs."),
}

def risk_map(records):
    records=[r for r in records if r.get("status") not in {"superseded","rejected"}]
    return [{"risk":risk,"designation":"analysis","implication":text,"field":field,
             "source_status":"supported" if any(r['status']=='supported' for r in records if r['field_name']==field) else "review_required",
             "sources":[r for r in records if r['field_name']==field and r.get('evidence')][:6]}
            for risk,(field,text) in RISKS.items()]
