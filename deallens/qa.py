"""Question routing is deterministic; answers come only from stored evidence."""
import re
from .catalog import QUESTIONS
from .term_comparison import SUPPORTED_STATUSES, compare_structured_terms

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

def _structured_components(terms, fields, strict, blocked):
    terms = [t for t in (terms or []) if t.get("schema_version") == "structured-terms/v1"
             and t.get("field_name") in fields]
    structured_conflicts = {row["field_name"] for row in compare_structured_terms(terms)
                            if row["classification"] == "conflict"}
    blocked.update(structured_conflicts)
    supported = []
    unresolved = []
    covered = set()
    for term in terms:
        eligible = (term.get("status") == "human_verified" if strict else
                    term.get("status") in SUPPORTED_STATUSES)
        open_items = list(term.get("unresolved") or [])
        for statement in term.get("statements") or []:
            open_items.extend(statement.get("unresolved") or [])
        if term.get("field_name") in blocked:
            eligible = False
            open_items.append({"reason": "cross_layer_conflict", "expression": term.get("field_name"),
                               "materiality": "material", "evidence": []})
        if eligible:
            for statement in term.get("statements") or []:
                supported.append({"field_name": term.get("field_name"),
                                  "term_id": term.get("term_id"),
                                  "document_layer": term.get("document_layer"),
                                  "review_status": term.get("review_status", "unreviewed"),
                                  "statement": statement})
            if not open_items:
                covered.add(term.get("field_name"))
        if not eligible:
            unresolved.append({"field_name": term.get("field_name"), "term_id": term.get("term_id"),
                               "reason": "strict_mode_exclusion" if strict else "interpretation_not_supported",
                               "status": term.get("status"), "items": open_items})
        elif open_items:
            unresolved.append({"field_name": term.get("field_name"), "term_id": term.get("term_id"),
                               "reason": "unresolved_components", "status": term.get("status"),
                               "items": open_items})
    return supported, unresolved, covered


def _component_text(component):
    statement = component["statement"]
    actor = statement.get("actor") or {}
    action = statement.get("action") or {}
    parts = [actor.get("name") or actor.get("role"), action.get("modality"),
             action.get("verb"), action.get("object")]
    if statement.get("conditions"):
        parts.append("conditions: " + ", ".join(c.get("text", "") for c in statement["conditions"]))
    if statement.get("exceptions"):
        parts.append("exceptions: " + ", ".join(c.get("text", "") for c in statement["exceptions"]))
    return " ".join(str(part) for part in parts if part)


def answer(question,records,comparisons,strict=False,structured_terms=()):
    records=[r for r in records if r.get("status") not in {"superseded","rejected"}]
    structured_terms=list(structured_terms or [])
    key=route(question)
    if not key:return {"question":question,"answer":UNSUPPORTED,"designation":"analysis","sources":[],"status":"unsupported"}
    fields=QUESTIONS[key];conflicts={c["field_name"] for c in comparisons if c["classification"]=="conflict"}
    blocked=[f for f in fields if f in conflicts]
    structured_supported, unresolved_components, structured_covered = _structured_components(
        structured_terms, fields, strict, set(blocked))
    for row in compare_structured_terms([t for t in structured_terms or [] if t.get("field_name") in fields]):
        if row["classification"] == "conflict" and row["field_name"] not in blocked:
            blocked.append(row["field_name"])
    supported=[r for r in records if r["field_name"] in fields and r["status"]=="supported" and r["field_name"] not in blocked and (not strict or r["review_status"]=="verified")]
    provisions=[r for r in records if r["field_name"] in fields and r["status"]=="source_excerpt" and r["field_name"] not in blocked and not strict]
    candidates=[r for r in records if r["field_name"] in fields and r.get("evidence") and r not in supported and r not in provisions]
    # Select at most one supported record per field/layer, keep conflicts visible.
    sources=[];seen=set()
    for r in supported:
        identity=(r["field_name"],r["document_layer"])
        if identity not in seen:sources.append(r);seen.add(identity)
    if not sources and not provisions and not structured_supported:
        return {"question":question,"answer":UNSUPPORTED,"status":"conflict" if blocked else "requires_review",
                "designation":"analysis","sources":[],"candidate_evidence":candidates[:18],
                "missing_fields":fields,"conflicting_fields":blocked,
                "supported_components":[], "unresolved_components":unresolved_components,
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
    values.extend(_component_text(component) for component in structured_supported)
    supported_fields = {r["field_name"] for r in sources} | structured_covered
    missing=[f for f in fields if f not in supported_fields]
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
    is_partial = bool(missing or provisions or unresolved_components or blocked)
    structured_unreviewed = any(c.get("review_status") != "verified" for c in structured_supported)
    designation = "source_excerpt" if provisions else ("fact" if sources or structured_supported else "analysis")
    return {"question":question,"answer":"; ".join(values),"status":"partial" if is_partial else "supported",
            "designation":designation,"sources":sources,"candidate_evidence":candidates[:18],
            "source_answers":source_answers,"excerpt_fields":sorted({r["field_name"] for r in provisions}),
            "supported_components":structured_supported,"unresolved_components":unresolved_components,
            "missing_fields":missing,"conflicting_fields":blocked,"review_status":"unreviewed" if provisions or structured_unreviewed or any(r['review_status']!='verified' for r in sources) else "verified",
            "note":"Partial answers do not establish absent terms. Source excerpts preserve contractual wording but are not a complete interpretation. Machine-supported is not human-verified."}
