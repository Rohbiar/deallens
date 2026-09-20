"""First-order financing cost sensitivities, not derivative fair-value pricing."""
from __future__ import annotations
from datetime import date
import re
import math
from .extract import DATE, date_iso

STRATEGIES=("unhedged","forward_starting_payer_swap","payer_option","deal_contingent_payer_swap")

def validate(a):
    for key,value in a.items():
        if isinstance(value,(int,float)) and not isinstance(value,bool) and not math.isfinite(value):
            raise ValueError(f"Non-finite assumption: {key}")
    if a["notional"]<=0 or a["dv01_per_100mm"]<=0:raise ValueError("Notional and DV01 must be positive")
    ps=[a[k] for k in ("base_probability","delay_probability","failure_probability")]
    if any(p<0 or p>1 for p in ps) or abs(sum(ps)-1)>1e-9:raise ValueError("Outcome probabilities must sum to one")
    if a["currency"] not in {"USD","EUR"}:raise ValueError("Unsupported or unresolved currency")
    if a["bond_spread_reference"]!="benchmark":raise ValueError("Only benchmark-quoted bond spreads implemented")

def scenario(a, strategy, benchmark_bp=0, swap_spread_bp=0, credit_bp=0, completed=True, delay_days=0):
    validate(a)
    if any(type(v) not in {int,float} or not math.isfinite(v) for v in (benchmark_bp,swap_spread_bp,credit_bp,delay_days)):
        raise ValueError("Scenario shocks and delay must be finite numbers")
    if strategy not in STRATEGIES:raise ValueError("Unknown strategy")
    if delay_days<0:raise ValueError("Negative delay")
    n=a["notional"];dv01=n/100_000_000*a["dv01_per_100mm"]
    bond_cost=dv01*(benchmark_bp+credit_bp) if completed else 0
    annual_increment=n*(benchmark_bp+credit_bp)/10000 if completed else 0
    swap_pnl=dv01*(benchmark_bp+swap_spread_bp)
    premium=0;hedge_pnl=0;timing_cost=0
    if strategy=="forward_starting_payer_swap":
        hedge_pnl=swap_pnl
        timing_cost=dv01*a["roll_cost_bp_per_90_days"]*delay_days/90
    elif strategy=="payer_option":
        # ATM payer option at evaluation expiry; premium given, not model-priced.
        hedge_pnl=max(swap_pnl,0)
        premium=n*a["option_premium_bp_notional"]/10000
        timing_cost=n*a["option_renewal_bp_per_90_days"]/10000*delay_days/90
    elif strategy=="deal_contingent_payer_swap":
        # Synthetic contract: fee paid upfront in all outcomes; no settlement on failure.
        hedge_pnl=swap_pnl if completed else 0
        premium=n*a["contingent_fee_bp_notional"]/10000
        timing_cost=dv01*a["roll_cost_bp_per_90_days"]*delay_days/90 if completed else 0
    return {"strategy":strategy,"currency":a["currency"],"designation":"analysis",
            "benchmark_bp":benchmark_bp,"swap_spread_bp":swap_spread_bp,"credit_bp":credit_bp,
            "completed":completed,"delay_days":delay_days,"dv01":dv01,
            "benchmark_cost_pv":dv01*benchmark_bp if completed else 0,
            "issuer_credit_cost_pv":dv01*credit_bp if completed else 0,
            "bond_cost_pv":bond_cost,"annual_coupon_increment":annual_increment,
            "hedge_pnl":hedge_pnl,"premium_or_fee":premium,"timing_cost":timing_cost,
            "net_incremental_cost_pv":bond_cost-hedge_pnl+premium+timing_cost,
            "failure_unwind_cash_cost":-hedge_pnl if not completed else None,
            "assumptions_version":a["version"]}

def extension_dates(records):
    """Conservative dates expressly attached to extension language.

    These are candidate scenario anchors, still require legal review. Never
    transform cure periods or regulatory deadlines into closing dates.
    """
    anchors={}
    for r in records:
        if r.get("status") in {"superseded","rejected"}:continue
        if r["field_name"]!="extension_dates_and_conditions" or not r.get("evidence"):continue
        if r["document_layer"]!="transaction-agreement":continue
        text=r["evidence"]
        patterns=[r'(?:to|until)\s+('+DATE+r')',r'then to\s+('+DATE+r')']
        if not re.search(r'extend|extension',text,re.I):continue
        for pattern in patterns:
            for m in re.finditer(pattern,text,re.I):
                iso=date_iso(m.group(1))
                if iso:anchors.setdefault(iso,r["locator"])
    return [{"date":d,"locator":anchors[d],"review_status":"unreviewed","designation":"assumption",
             "note":"Hypothetical closing scenario at an expressly stated extension date; does not assert that extension conditions have been satisfied."} for d in sorted(anchors)]

def run_analytics(doc,records,comparisons,config):
    supported_money=[r for r in records if r["field_name"]=="consideration_per_share" and r["status"]=="supported"]
    currencies={r["currency"] for r in supported_money}
    currency=next(iter(currencies)) if len(currencies)==1 else None
    # The only case-specific branch applies the expressly required assignment inputs.
    a=dict(config["bio_techne"] if doc["role"]=="development" else config["validation_template"])
    if a["currency"]=="from_supported_consideration":a["currency"]=currency
    a["version"]=config["version"]
    if a["currency"] is None:return {"status":"blocked","reason":"Consideration currency is unresolved; cannot label analytics."}
    validate(a)
    inputs=[("base",0,0,0,True,0),("rates_up_25",25,0,0,True,0),
            ("rates_down_25",-25,0,0,True,0),("rates_up_50",50,0,0,True,0),
            ("rates_up_25_credit_wider_20",25,0,20,True,0),
            ("swap_spread_wider_10",0,10,0,True,0),
            ("failure_rates_down_25",-25,0,0,False,0),("failure_rates_up_25",25,0,0,False,0)]
    anchors=extension_dates(records)
    outside=[c["canonical_value"] for c in comparisons if c["field_name"]=="outside_or_long_stop_date" and c["canonical_value"]]
    anchors=[x for x in anchors if not outside or x["date"]>outside[0]]
    unresolved=[]
    for label,anchor in [("first_extension",anchors[0] if anchors else None),("final_extension",anchors[-1] if anchors else None)]:
        if anchor:
            days=(date.fromisoformat(anchor["date"])-date.fromisoformat(a["issue_date"])).days
            if days>=0:inputs.append((label,25,0,0,True,days))
            else:unresolved.append({"scenario":label,"status":"blocked","reason":"Anchor precedes synthetic issue date"})
        else:unresolved.append({"scenario":label,"status":"blocked","reason":"No safely normalized extension date; inspect timeline. No synthetic contract date substituted."})
    rows=[]
    for name,b,s,c,done,delay in inputs:
        for strategy in STRATEGIES:
            rows.append({"scenario_id":name,**scenario(a,strategy,b,s,c,done,delay)})
    expected=[]
    # Only compute a defined mutually exclusive joint scenario distribution.
    for strategy in STRATEGIES:
        selected={r["scenario_id"]:r for r in rows if r["strategy"]==strategy}
        if "first_extension" not in selected:
            expected.append({"strategy":strategy,"status":"blocked","reason":"Delay-state cashflow missing"});continue
        weights={"rates_up_25":a["base_probability"],"first_extension":a["delay_probability"],"failure_rates_down_25":a["failure_probability"]}
        expected.append({"strategy":strategy,"status":"synthetic_joint_distribution",
                         "weights":weights,"expected_incremental_cost_pv":sum(selected[k]["net_incremental_cost_pv"]*w for k,w in weights.items()),
                         "note":"Explicitly assumes +25bp on base/delay success and -25bp on failure. Not a market forecast; no double-counting overlapping stresses."})
    adaptation={"structure":doc["transaction_type"],"currency":a["currency"],
                "interpretation":"Fixed-rate refinancing sensitivity on a synthetic financing slice. Review source funding obligations separately.",
                "disclosed_bridge":None}
    bridge=[r for r in records if r["field_name"]=="bridge_amount" and r["status"]=="supported"]
    if a["currency"]=="EUR":
        x=config["cross_currency_template"];exposure=a["notional"]*x["fx_funding_share"]
        adaptation.update({"fx_assumptions":x,"eur_amount_requiring_usd":exposure,
                           "usd_cost_at_synthetic_spot":exposure*x["usd_per_eur"],
                           "usd_increment_on_eur_appreciation":exposure*x["usd_per_eur"]*x["fx_shock_fraction"],
                           "fx_note":"Same-currency EUR debt naturally funds the assumed EUR portion; remaining USD-funded portion has EUR appreciation risk. Rate hedges do not hedge FX."})
        if bridge:
            b=bridge[0];draw=b["normalized_value"]*x["bridge_draw_fraction"]
            adaptation["disclosed_bridge"]={"amount":b["normalized_value"],"currency":b["currency"],"source":b,
                "assumed_draw":draw,"annualized_interest_initial":draw*(x["euribor"]+x["bridge_margin"]),
                "annualized_interest_after_three_synthetic_stepups":draw*(x["euribor"]+x["bridge_margin"]+3*x["bridge_stepup_bp_per_90_days"]/10000),
                "annualized_increment_if_euribor_up_25":draw*0.0025,
                "note":"Annualized run rates, not 364-day cashflow totals. Fees and exact rating schedule excluded; bridge is separate from synthetic fixed-rate refinancing slice."}
    return {"status":"illustrative","assumptions":a,"rows":rows,"extension_anchors":anchors,
            "blocked_scenarios":unresolved,"expected_costs":expected,"adaptation":adaptation,
            "baseline_coupon":a["benchmark_rate"]+a["issuer_credit_spread"],
            "initial_swap_spread":a["swap_rate"]-a["benchmark_rate"],
            "sign_convention":"Positive net cost is worse for issuer; positive hedge P&L is a receipt. Costs are changes relative to unhedged baseline, not bond mark-to-market losses.",
            "limitations":["Constant DV01 linearization; no convexity, discount curve, carry or credit curve construction.",
                           "Spot rates supplied; using them as forward reference levels is synthetic, not a forward curve.",
                           "Option payoff is expiry intrinsic value with assumed premium; no volatility-based fair value.",
                           "Deal-contingent hedge terms are synthetic. Actual failure definitions, extensions, exclusions, fees and documentation require negotiation.",
                           "No automatic hedge recommendation or trade execution; no contractual termination fee offsets assumed."]}
