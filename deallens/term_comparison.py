"""Fail-closed comparison helpers for ``structured-terms/v1`` records.

These helpers compare legal components, not prose similarity.  A candidate,
unresolved dependency, or omitted layer prevents a ``match`` classification.
"""
from collections import defaultdict
import json


SUPPORTED_STATUSES = {"machine_supported", "human_verified"}


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), default=str)


def statement_components(statement):
    """Return the legally material components used for equality checks."""
    action = statement.get("action") or {}
    actor = statement.get("actor") or {}
    beneficiary = statement.get("beneficiary") or {}
    return {
        "kind": statement.get("kind"),
        "actor": {"name": actor.get("name"), "role": actor.get("role")},
        "modality": action.get("modality"),
        "action": {"verb": action.get("verb"), "object": action.get("object")},
        "beneficiary": {"name": beneficiary.get("name"),
                        "role": beneficiary.get("role")} if beneficiary else None,
        "trigger": statement.get("trigger"),
        "conditions": [_condition_value(item) for item in statement.get("conditions") or []],
        "exceptions": [_condition_value(item) for item in statement.get("exceptions") or []],
        "business_scope": statement.get("business_scope"),
        "amount": _without_evidence(statement.get("amount")),
        "timing": _without_evidence(statement.get("timing")),
    }


def _without_evidence(value):
    if not isinstance(value, dict):
        return value
    return {key: item for key, item in value.items() if key != "evidence"}


def _condition_value(value):
    return _without_evidence(value)


def _open_items(term):
    items = list(term.get("unresolved") or [])
    for statement in term.get("statements") or []:
        items.extend(statement.get("unresolved") or [])
    return items


def compare_structured_terms(terms):
    """Compare structured records across source layers.

    Results intentionally use ``unresolved`` whenever uncertainty is present.
    Two supported records are a match only when every material component,
    including actor, modality, conditions, and exceptions, is equal.
    """
    grouped = defaultdict(list)
    for term in terms or []:
        if term.get("schema_version") == "structured-terms/v1":
            grouped[term.get("field_name")].append(term)
    rows = []
    for field_name, records in grouped.items():
        summary = [r for r in records if r.get("document_layer") == "8-k-summary"]
        agreement = [r for r in records if r.get("document_layer") != "8-k-summary"]
        supported = [r for r in records if r.get("status") in SUPPORTED_STATUSES]
        uncertain = [r for r in records if r.get("status") not in SUPPORTED_STATUSES or _open_items(r)]
        classification = "unresolved"
        differences = []
        if not uncertain and summary and agreement and len(supported) == len(records):
            left = sorted(_canonical(statement_components(s))
                          for r in summary for s in r.get("statements", []))
            right = sorted(_canonical(statement_components(s))
                           for r in agreement for s in r.get("statements", []))
            if left == right:
                classification = "match"
            else:
                classification = "conflict"
                differences = _component_differences(summary, agreement)
        rows.append({
            "field_name": field_name,
            "classification": classification,
            "summary": summary,
            "agreement": agreement,
            "differences": differences,
            "uncertainty": [
                {"term_id": r.get("term_id"), "status": r.get("status"),
                 "unresolved": _open_items(r)} for r in uncertain
            ],
            "canonical_value": None,
        })
    return sorted(rows, key=lambda row: row["field_name"] or "")


def _component_differences(summary, agreement):
    left = [statement_components(s) for r in summary for s in r.get("statements", [])]
    right = [statement_components(s) for r in agreement for s in r.get("statements", [])]
    keys = ("kind", "actor", "modality", "action", "beneficiary", "trigger",
            "conditions", "exceptions", "business_scope", "amount", "timing")
    differences = []
    for index in range(max(len(left), len(right))):
        a = left[index] if index < len(left) else None
        b = right[index] if index < len(right) else None
        for key in keys:
            av = a.get(key) if a else None
            bv = b.get(key) if b else None
            if _canonical(av) != _canonical(bv):
                differences.append({"statement_index": index, "component": key,
                                    "summary": av, "agreement": bv})
    return differences


# Readable alias for coordinator wiring.
structured_term_comparison = compare_structured_terms
