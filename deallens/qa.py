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
    records=[r for r in records if r.get("status") not in {"superseded","rejected"}]
    key=route(question)
    if not key:return {"question":question,"answer":UNSUPPORTED,"designation":"analysis","sources":[],"status":"unsupported"}
    fields=QUESTIONS[key];conflicts={c["field_name"] for c in comparisons if c["classification"]=="conflict"}
    blocked=[f for f in fields if f in conflicts]
    supported=[r for r in records if r["field_name"] in fields and r["status"]=="supported" and r["field_name"] not in conflicts and (not strict or r["review_status"]=="verified")]
    provisions=[r for r in records if r["field_name"] in fields and r["status"]=="source_excerpt" and r["field_name"] not in conflicts and not strict]
    candidates=[r for r in records if r["field_name"] in fields and r.get("evidence") and r not in supported and r not in provisions]
    # Select at most one supported record per field/layer, keep conflicts visible.
    sources=[];seen=set()
    for r in supported:
        identity=(r["field_name"],r["document_layer"])
        if identity not in seen:sources.append(r);seen.add(identity)
    if not sources and not provisions:
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
                value=r["normalized_value"]
                if isinstance(value,dict) and isinstance(value.get("summary"),str):value=value["summary"]
                values.append(f"{f}: {qualifier}{value}"+(f" {r['currency']}" if r.get('currency') else ""))
    missing=[f for f in fields if f not in {r["field_name"] for r in sources}]
    # Whole sections never count as a completed interpretation or an inferred
    # absence of a required field.
    source_answers=[]
    for r in provisions:
        source_answers.append({"field_name":r["field_name"],"document_layer":r["document_layer"],
            "sections":r["candidate_value"]["sections"],"designation":"source_excerpt",
            "sources":r["evidence_sources"],"reference_context":r["reference_context"],
            "definition_context":r.get("definition_context",[]),
            "completeness":r["completeness"],"limitations":r["limitations"]})
    if source_answers:
        values.append("The agreement provisions are reproduced below, including continuation pages and available cross-references. Their complete legal interpretation remains unresolved.")
    return {"question":question,"answer":"; ".join(values),"status":"partial" if missing else "supported",
            "designation":"fact" if sources and not provisions else "source_excerpt","sources":sources,"candidate_evidence":candidates[:18],
            "source_answers":source_answers,"excerpt_fields":sorted({r["field_name"] for r in provisions}),
            "missing_fields":missing,"conflicting_fields":blocked,"review_status":"unreviewed" if provisions or any(r['review_status']!='verified' for r in sources) else "verified",
            "note":"Partial answers do not establish absent terms. Source excerpts preserve contractual wording but are not a complete interpretation. Machine-supported is not human-verified."}
