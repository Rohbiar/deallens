"""Timeline projection for conditional structured legal terms."""

from .term_comparison import SUPPORTED_STATUSES


TIMELINE_KINDS = {"extension", "fee_trigger", "fee_tail", "remedy",
                  "financing_condition"}


def structured_term_timeline(terms, strict=False):
    """Project terms into events without asserting that an event occurred."""
    events = []
    for term in terms or []:
        if term.get("schema_version") != "structured-terms/v1":
            continue
        usable = (term.get("status") == "human_verified" if strict else
                  term.get("status") in SUPPORTED_STATUSES)
        for statement in term.get("statements") or []:
            if statement.get("kind") not in TIMELINE_KINDS:
                continue
            action = statement.get("action") or {}
            actor = statement.get("actor") or {}
            timing = statement.get("timing")
            unresolved = list(term.get("unresolved") or []) + list(statement.get("unresolved") or [])
            events.append({
                "event": statement.get("statement_id"),
                "field_name": term.get("field_name"),
                "kind": statement.get("kind"),
                "actor": {"name": actor.get("name"), "role": actor.get("role")},
                "modality": action.get("modality"),
                "action": {"verb": action.get("verb"), "object": action.get("object")},
                "election_required": action.get("modality") == "permitted",
                "automatic": action.get("modality") == "automatic",
                "conditions": statement.get("conditions") or [],
                "exceptions": statement.get("exceptions") or [],
                "timing": timing,
                "contractual_date": (timing or {}).get("value")
                    if (timing or {}).get("clock_type") == "absolute" else None,
                "occurrence_status": "not_established",
                "support_status": "supported" if usable and not unresolved else "unresolved",
                "unresolved": unresolved,
                "evidence": statement.get("evidence") or [],
                "term_id": term.get("term_id"),
            })
    return events


term_timeline = structured_term_timeline
