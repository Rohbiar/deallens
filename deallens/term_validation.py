"""Fail-closed validation for structured provision candidates."""
import json
import math

from .structured_terms import (CONTEXT_SCHEMA_VERSION, MODALITIES,
                               PRIORITY_FIELDS, SCHEMA_VERSION,
                               STATEMENT_KINDS, TERM_STATUSES,
                               UNRESOLVED_MATERIALITIES)


def validate_term(term, context_bundle, reference_assertions=()):
    """Return deterministic errors and support eligibility.

    ``reference_assertions`` are independently prepared atomic expectations used
    in tests/evaluation.  Empty assertions can validate shape and provenance but
    can never establish semantic support.
    """
    errors = []
    warnings = []
    _json_safe(term, errors)
    _check_header(term, context_bundle, errors)
    source_ids = {source.get("source_id") for source in context_bundle.get("sources", [])}
    statement_ids = set()
    for index, stmt in enumerate(term.get("statements", [])):
        path = f"statements[{index}]"
        _check_statement(stmt, path, source_ids, errors)
        statement_id = stmt.get("statement_id")
        if statement_id in statement_ids:
            errors.append(f"{path}.statement_id: duplicate")
        statement_ids.add(statement_id)
    _check_field_semantics(term.get("field_name"), term.get("statements", []), errors)
    _check_unresolved(term.get("unresolved", []), "unresolved", source_ids, errors)
    _check_contradictions(term.get("statements", []), errors)
    for assertion in reference_assertions:
        _check_assertion(term, assertion, errors)

    interpretation_open = list(term.get("unresolved", []))
    for statement in term.get("statements", []):
        interpretation_open.extend(statement.get("unresolved", []))
    material_open = any(item.get("materiality") != "non_material"
                        for item in interpretation_open)
    context_open = bool(context_bundle.get("unresolved")) or bool(
        context_bundle.get("budget", {}).get("truncated"))
    basis = set(term.get("validation_basis", []))
    semantic_basis = bool(reference_assertions) and "independent_atomic_assertions" in basis
    eligible = not errors and not material_open and not context_open and semantic_basis
    if not reference_assertions:
        warnings.append("semantic_support_not_evaluated")
    if context_open:
        warnings.append("retrieval_context_unresolved")
    if material_open:
        warnings.append("material_interpretation_unresolved")
    if term.get("status") in {"machine_supported", "human_verified"} and not eligible:
        errors.append("status: support claimed without complete validation basis")
        eligible = False
    return {"valid": not errors, "errors": errors, "warnings": warnings,
            "machine_support_eligible": eligible}


def _json_safe(value, errors):
    try:
        json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError):
        errors.append("record: not finite JSON")


def _check_header(term, context, errors):
    if term.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version: unsupported")
    if term.get("field_name") not in PRIORITY_FIELDS:
        errors.append("field_name: unsupported structured field")
    if term.get("status") not in TERM_STATUSES:
        errors.append("status: invalid")
    if term.get("document_id") != context.get("document_id"):
        errors.append("document_id: context mismatch")
    if term.get("document_sha256") != context.get("source_hash"):
        errors.append("document_sha256: context mismatch")
    if context.get("schema_version") != CONTEXT_SCHEMA_VERSION:
        errors.append("context.schema_version: unsupported")
    if term.get("context", {}).get("source_hash") != context.get("source_hash"):
        errors.append("context.source_hash: mismatch")
    roots = set(context.get("root_section_ids", []))
    if set(term.get("context", {}).get("root_section_ids", [])) != roots:
        errors.append("context.root_section_ids: mismatch")
    statements = term.get("statements")
    if not isinstance(statements, list):
        errors.append("statements: list required")
    elif not statements:
        material_unresolved = any(
            isinstance(item, dict) and item.get("materiality") == "material"
            for item in term.get("unresolved", [])
        )
        if term.get("status") != "unresolved" or not material_unresolved:
            errors.append("statements: empty only for materially unresolved term")
    if term.get("review_status") == "verified" and term.get("status") != "human_verified":
        errors.append("review_status: cannot self-verify")


def _check_statement(stmt, path, source_ids, errors):
    if stmt.get("kind") not in STATEMENT_KINDS:
        errors.append(f"{path}.kind: invalid")
    if not stmt.get("statement_id"):
        errors.append(f"{path}.statement_id: required")
    actor = stmt.get("actor")
    if not isinstance(actor, dict) or not actor.get("name") or not actor.get("role"):
        errors.append(f"{path}.actor: resolved name and role required")
    action = stmt.get("action")
    if not isinstance(action, dict) or action.get("modality") not in MODALITIES:
        errors.append(f"{path}.action.modality: invalid")
    if not isinstance(action, dict) or not action.get("verb") or not action.get("object"):
        errors.append(f"{path}.action: verb and object required")
    beneficiary = stmt.get("beneficiary")
    if beneficiary is not None and (not isinstance(beneficiary, dict)
                                    or not beneficiary.get("name")
                                    or not beneficiary.get("role")):
        errors.append(f"{path}.beneficiary: resolved name and role required")
    trigger = stmt.get("trigger")
    if trigger is not None:
        if not isinstance(trigger, dict) or not trigger.get("event"):
            errors.append(f"{path}.trigger.event: required")
        else:
            _check_evidence(trigger.get("evidence"), f"{path}.trigger.evidence",
                            source_ids, errors, required=True)
    _check_evidence(stmt.get("evidence"), f"{path}.evidence", source_ids, errors, required=True)
    for key in ("conditions", "exceptions"):
        values = stmt.get(key)
        if not isinstance(values, list):
            errors.append(f"{path}.{key}: list required")
            continue
        for item in values:
            if not isinstance(item, dict) or not item.get("condition_id") or not item.get("text"):
                errors.append(f"{path}.{key}: invalid condition")
            else:
                _check_evidence(item.get("evidence"), f"{path}.{key}.evidence",
                                source_ids, errors)
    timing = stmt.get("timing")
    if timing is not None:
        if timing.get("unit") not in {None, "calendar_days", "business_days", "months", "years", "date"}:
            errors.append(f"{path}.timing.unit: invalid")
        if timing.get("unit") and timing.get("value") is None:
            errors.append(f"{path}.timing.value: required with unit")
        if timing.get("unit") in {"calendar_days", "business_days", "months", "years"}:
            value = timing.get("value")
            if type(value) not in {int, float} or not math.isfinite(value) or value < 0:
                errors.append(f"{path}.timing.value: invalid numeric duration")
        _check_evidence(timing.get("evidence"), f"{path}.timing.evidence", source_ids, errors)
    amount = stmt.get("amount")
    if amount is not None:
        value = amount.get("value")
        if type(value) not in {int, float} or not math.isfinite(value) or value < 0:
            errors.append(f"{path}.amount.value: invalid")
        if not amount.get("currency") or amount.get("qualifier") not in {"exact", "at_least", "at_most"}:
            errors.append(f"{path}.amount: currency and qualifier required")
        _check_evidence(amount.get("evidence"), f"{path}.amount.evidence", source_ids, errors)
    _check_unresolved(stmt.get("unresolved", []), f"{path}.unresolved", source_ids, errors)


def _check_field_semantics(field_name, statements, errors):
    """Enforce relationships that shape-only validation cannot express."""
    for index, stmt in enumerate(statements):
        path = f"statements[{index}]"
        kind = stmt.get("kind")
        action = stmt.get("action") or {}
        actor = stmt.get("actor") or {}
        if field_name == "extension_dates_and_conditions":
            if kind != "extension":
                errors.append(f"{path}.kind: extension required for field")
            if action.get("verb") not in {"extend", "elect to extend",
                                          "agree in writing to extend",
                                          "authorize later date"}:
                errors.append(f"{path}.action.verb: extension action required")
            if action.get("modality") == "automatic" and actor.get("role") != "automatic_mechanism":
                errors.append(f"{path}.actor.role: automatic extension cannot be a party election")
            if action.get("modality") != "automatic" and actor.get("role") == "automatic_mechanism":
                errors.append(f"{path}.action.modality: automatic mechanism requires automatic modality")
        elif field_name == "fee_triggers_and_tails":
            if kind not in {"fee_trigger", "fee_tail"}:
                errors.append(f"{path}.kind: fee trigger or tail required for field")
            if action.get("verb") != "pay" or action.get("modality") != "required":
                errors.append(f"{path}.action: fee payment obligation required")
            if not stmt.get("beneficiary"):
                errors.append(f"{path}.beneficiary: fee payee required")
            if not stmt.get("trigger"):
                errors.append(f"{path}.trigger: fee trigger required")
            if kind == "fee_tail":
                timing = stmt.get("timing") or {}
                if timing.get("unit") != "months" or timing.get("anchor") != "termination":
                    errors.append(f"{path}.timing: fee tail requires months after termination")
        elif field_name == "remedy_limitations":
            if kind != "remedy":
                errors.append(f"{path}.kind: remedy required for field")
            if action.get("modality") not in {"required", "permitted", "prohibited"}:
                errors.append(f"{path}.action.modality: remedy modality required")
            if not stmt.get("trigger"):
                errors.append(f"{path}.trigger: remedy trigger required")
            scope = stmt.get("business_scope") or {}
            if not scope.get("scope") or not scope.get("limit"):
                errors.append(f"{path}.business_scope: remedy scope and limit required")
            if not stmt.get("exceptions"):
                errors.append(f"{path}.exceptions: remedy limitation required")
        elif field_name == "award_cohort_differences":
            if kind != "award_treatment":
                errors.append(f"{path}.kind: award treatment required for field")
            scope = stmt.get("business_scope") or {}
            if not scope.get("award_type") or not scope.get("cohort"):
                errors.append(f"{path}.business_scope: award type and cohort required")
            if not stmt.get("trigger"):
                errors.append(f"{path}.trigger: award treatment trigger required")
        elif field_name == "financing_conditions":
            if kind != "financing_condition":
                errors.append(f"{path}.kind: financing condition required for field")
            scope = stmt.get("business_scope") or {}
            condition_type = scope.get("condition_type")
            if condition_type not in {"transaction_closing_condition", "lender_funding_condition",
                                      "lender_certain_funds_restriction"}:
                errors.append(f"{path}.business_scope.condition_type: invalid")
            if condition_type == "lender_funding_condition":
                if actor.get("role") != "lender" or action.get("modality") != "conditional":
                    errors.append(f"{path}.action: lender funding condition must be conditional")
                if not stmt.get("conditions"):
                    errors.append(f"{path}.conditions: lender funding conditions required")
            if condition_type == "transaction_closing_condition" and action.get("modality") != "prohibited":
                errors.append(f"{path}.action.modality: no-financing closing condition must be prohibited")


def _check_evidence(refs, path, source_ids, errors, required=False):
    if not isinstance(refs, list) or (required and not refs):
        errors.append(f"{path}: {'nonempty ' if required else ''}list required")
        return
    for ref in refs:
        if not isinstance(ref, dict) or ref.get("source_id") not in source_ids:
            errors.append(f"{path}: unknown source_id")


def _check_unresolved(items, path, source_ids, errors):
    if not isinstance(items, list):
        errors.append(f"{path}: list required")
        return
    for item in items:
        if not isinstance(item, dict) or not item.get("reason") or not item.get("expression"):
            errors.append(f"{path}: invalid unresolved item")
            continue
        if item.get("materiality") not in UNRESOLVED_MATERIALITIES:
            errors.append(f"{path}.materiality: invalid")
        _check_evidence(item.get("evidence", []), f"{path}.evidence", source_ids, errors)


def _check_contradictions(statements, errors):
    seen = {}
    opposites = {"required": {"prohibited"}, "permitted": {"prohibited"},
                 "automatic": {"prohibited"},
                 "prohibited": {"required", "permitted", "automatic"}}
    for stmt in statements:
        actor = stmt.get("actor") or {}
        action = stmt.get("action") or {}
        key = (stmt.get("kind"), actor.get("name"), actor.get("role"),
               action.get("verb"), action.get("object"),
               json.dumps(stmt.get("trigger"), sort_keys=True, default=str),
               json.dumps(stmt.get("conditions"), sort_keys=True, default=str),
               json.dumps(stmt.get("exceptions"), sort_keys=True, default=str))
        modality = action.get("modality")
        if modality in opposites and seen.get(key) in opposites[modality]:
            errors.append("statements: contradictory modalities for same atomic assertion")
        seen[key] = modality


def _check_assertion(term, expected, errors):
    matches = [stmt for stmt in term.get("statements", [])
               if stmt.get("statement_id") == expected.get("statement_id")]
    if len(matches) != 1:
        errors.append(f"assertion {expected.get('statement_id')}: missing or duplicate")
        return
    stmt = matches[0]
    for key in ("actor", "action", "timing", "amount", "beneficiary", "business_scope"):
        for subkey, value in (expected.get(key) or {}).items():
            if (stmt.get(key) or {}).get(subkey) != value:
                errors.append(f"assertion {expected['statement_id']}: {key}.{subkey} mismatch")
    for key in ("required_condition_ids", "required_exception_ids"):
        actual_key = "conditions" if key == "required_condition_ids" else "exceptions"
        actual = {item.get("condition_id") for item in stmt.get(actual_key, [])}
        if not set(expected.get(key, [])).issubset(actual):
            errors.append(f"assertion {expected['statement_id']}: {actual_key} omitted")
