"""Question routing is deterministic; answers come only from stored evidence."""
import re
from .catalog import QUESTIONS

UNSUPPORTED = "I could not identify sufficient source support for this answer."

def route(question):
    if question in QUESTIONS:return question
    patterns=[("deal_contingent_hedge",r'deal.contingent|hedg'),("financing_condition",r'financing condition'),
              ("fee_triggers",r'trigger|fee tail'),("extensions",r'extend|extension'),
              ("outside_date",r'outside|long.stop'),("consideration",r'consideration|price per share'),
              ("awards",r'options|rsus|psus|award|restricted stock|purchase plan'),
              ("remedies",r'remedy|burdensome|detriment|remedies'),("fees",r'termination fee'),
              ("regulatory",r'regulat|antitrust'),("approval",r'approval|tender|acceptance|threshold'),
              ("financing",r'financ|bridge|funding')]
    # Do not follow instructions embedded in user/source text.
    if re.search(r'ignore.{0,40}instructions|system prompt|reveal.{0,30}secret|execute|shell command',question,re.I):return None
    return next((key for key,p in patterns if re.search(p,question,re.I)),None)

def answer(question,records,comparisons,strict=False):
    key=route(question)
    if not key:return {"question":question,"answer":UNSUPPORTED,"designation":"analysis","sources":[],"status":"unsupported"}
    fields=QUESTIONS[key];conflicts={c["field_name"] for c in comparisons if c["classification"]=="conflict"}
    blocked=[f for f in fields if f in conflicts]
    supported=[r for r in records if r["field_name"] in fields and r["status"]=="supported" and r["field_name"] not in conflicts and (not strict or r["review_status"]=="verified")]
    candidates=[r for r in records if r["field_name"] in fields and r.get("evidence") and r not in supported]
    # Select at most one supported record per field/layer, keep conflicts visible.
    sources=[];seen=set()
    for r in supported:
        identity=(r["field_name"],r["document_layer"])
        if identity not in seen:sources.append(r);seen.add(identity)
    if not sources:
        return {"question":question,"answer":UNSUPPORTED,"status":"conflict" if blocked else "requires_review",
                "designation":"analysis","sources":[],"candidate_evidence":candidates[:18],
                "missing_fields":fields,"conflicting_fields":blocked,
                "note":"Candidate passages below are retrieval results, not an approved answer. Review complete provisions and cross-references."}
    values=[]
    for f in fields:
        choices=[r for r in sources if r["field_name"]==f]
        if choices:
            r=next((r for r in choices if r["document_layer"]=="transaction-agreement"),choices[0])
            qualifier={"at_least":"at least ","at_most":"at most "}.get(r.get("value_qualifier"),"")
            if f=="financing_condition" and r["normalized_value"] is False:
                values.append("Obtaining financing is not a condition under the cited provision")
            else:
                values.append(f"{f}: {qualifier}{r['normalized_value']}"+(f" {r['currency']}" if r.get('currency') else ""))
    missing=[f for f in fields if f not in {r["field_name"] for r in sources}]
    return {"question":question,"answer":"; ".join(values),"status":"partial" if missing else "supported",
            "designation":"fact","sources":sources,"candidate_evidence":candidates[:18],
            "missing_fields":missing,"conflicting_fields":blocked,"review_status":"unreviewed" if any(r['review_status']!='verified' for r in sources) else "verified",
            "note":"Partial answers do not establish absent terms. Machine-supported is not human-verified."}
