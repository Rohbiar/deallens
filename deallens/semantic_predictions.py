"""Fail-closed adapter from structured terms to semantic predictions.

The Package D reference vocabulary is deliberately not imported here.  Callers
provide transparent case descriptors that identify a document, field and the
structured paths to expose.  Descriptors contain no expected values, so this
adapter cannot manufacture a benchmark answer or tune extraction to the frozen
challenge set.
"""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any, Iterable


PREDICTION_SCHEMA_VERSION = "1.0"
STRUCTURED_TERM_SCHEMA_VERSION = "structured-terms/v1"
SUPPORTED_TERM_STATUSES = {"machine_supported", "human_verified"}
ALLOWED_DIMENSIONS = {"actor", "obligation", "trigger", "exception", "timing", "scope"}
ALLOWED_TRANSFORMS = {"identity", "condition_texts", "party_names"}
_PATH_PART = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_MISSING = object()


def build_semantic_predictions(
    terms: Iterable[dict[str, Any]],
    case_descriptors: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    """Adapt eligible structured terms to Package D's prediction envelope.

    A candidate, explicitly unresolved term, materially unresolved dependency,
    ambiguous term/statement selection, or unavailable mapped value makes the
    whole case ``unresolved``.  An absent term is an ``abstention``.  Only clean
    ``machine_supported`` and ``human_verified`` terms may assert values.

    Each assertion descriptor has this transparent shape::

        {
          "assertion_id": "example_actor",
          "dimension": "actor",
          "statement_selector": {"kind": "extension"},
          "source_path": "actor.name",
          "transform": "identity"
        }

    Selectors and paths refer only to the generic structured-terms/v1 schema.
    They never contain an expected benchmark value.
    """
    term_list = list(terms)
    descriptors = list(case_descriptors)
    _validate_descriptors(descriptors)

    predictions = []
    for descriptor in descriptors:
        matches = [term for term in term_list if _term_matches(term, descriptor)]
        if not matches:
            predictions.append(_status_case(descriptor["case_id"], "abstention"))
            continue
        if len(matches) != 1 or not _term_can_assert(matches[0]):
            predictions.append(_status_case(descriptor["case_id"], "unresolved"))
            continue

        assertions = _map_assertions(matches[0], descriptor["assertions"])
        if assertions is None:
            predictions.append(_status_case(descriptor["case_id"], "unresolved"))
        else:
            predictions.append({
                "case_id": descriptor["case_id"],
                "status": "supported",
                "assertions": assertions,
            })
    return {"schema_version": PREDICTION_SCHEMA_VERSION, "cases": predictions}


def _status_case(case_id: str, status: str) -> dict[str, Any]:
    return {"case_id": case_id, "status": status, "assertions": []}


def _term_matches(term: dict[str, Any], descriptor: dict[str, Any]) -> bool:
    if term.get("schema_version") != STRUCTURED_TERM_SCHEMA_VERSION:
        return False
    for key in ("document_id", "field_name", "document_layer"):
        expected = descriptor.get(key)
        if expected is not None and term.get(key) != expected:
            return False
    return True


def _term_can_assert(term: dict[str, Any]) -> bool:
    if term.get("status") not in SUPPORTED_TERM_STATUSES:
        return False
    if term.get("status") == "human_verified" and term.get("review_status") != "verified":
        return False
    statements = term.get("statements")
    if not isinstance(statements, list) or not statements:
        return False
    open_items = list(term.get("unresolved") or [])
    for statement in statements:
        if not isinstance(statement, dict):
            return False
        open_items.extend(statement.get("unresolved") or [])
    return not any(
        not isinstance(item, dict) or item.get("materiality") != "non_material"
        for item in open_items
    )


def _map_assertions(
    term: dict[str, Any], assertion_descriptors: list[dict[str, Any]]
) -> list[dict[str, Any]] | None:
    if not assertion_descriptors:
        return None
    mapped = []
    statements = term["statements"]
    for descriptor in assertion_descriptors:
        selector = descriptor.get("statement_selector", {})
        matches = [statement for statement in statements
                   if _selector_matches(statement, selector)]
        if len(matches) != 1:
            return None
        value = _read_path(matches[0], descriptor["source_path"])
        if value is _MISSING:
            return None
        value = _transform(value, descriptor.get("transform", "identity"))
        if value is _MISSING:
            return None
        mapped.append({
            "assertion_id": descriptor["assertion_id"],
            "value": deepcopy(value),
        })
    return mapped


def _selector_matches(statement: dict[str, Any], selector: dict[str, Any]) -> bool:
    return all(_read_path(statement, path) == expected
               for path, expected in selector.items())


def _read_path(value: Any, path: str) -> Any:
    current = value
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _transform(value: Any, name: str) -> Any:
    if name == "identity":
        return value
    if name == "condition_texts":
        if not isinstance(value, list) or not all(
            isinstance(item, dict) and isinstance(item.get("text"), str) for item in value
        ):
            return _MISSING
        return [item["text"] for item in value]
    if name == "party_names":
        if not isinstance(value, list) or not all(
            isinstance(item, dict) and isinstance(item.get("name"), str) for item in value
        ):
            return _MISSING
        return [item["name"] for item in value]
    return _MISSING


def _validate_descriptors(descriptors: list[dict[str, Any]]) -> None:
    case_ids = set()
    for descriptor in descriptors:
        case_id = descriptor.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            raise ValueError(f"invalid or duplicate case_id: {case_id!r}")
        case_ids.add(case_id)
        if not isinstance(descriptor.get("document_id"), str) or not descriptor["document_id"]:
            raise ValueError(f"{case_id}: document_id is required")
        if not isinstance(descriptor.get("field_name"), str) or not descriptor["field_name"]:
            raise ValueError(f"{case_id}: field_name is required")
        assertions = descriptor.get("assertions")
        if not isinstance(assertions, list):
            raise ValueError(f"{case_id}: assertion mappings must be a list")
        assertion_ids = set()
        for assertion in assertions:
            assertion_id = assertion.get("assertion_id")
            if (not isinstance(assertion_id, str) or not assertion_id
                    or assertion_id in assertion_ids):
                raise ValueError(f"{case_id}: invalid or duplicate assertion_id")
            assertion_ids.add(assertion_id)
            if assertion.get("dimension") not in ALLOWED_DIMENSIONS:
                raise ValueError(f"{case_id}/{assertion_id}: invalid dimension")
            source_path = assertion.get("source_path")
            if not _valid_path(source_path):
                raise ValueError(f"{case_id}/{assertion_id}: invalid source_path")
            selector = assertion.get("statement_selector", {})
            if not isinstance(selector, dict) or not all(_valid_path(path) for path in selector):
                raise ValueError(f"{case_id}/{assertion_id}: invalid statement_selector")
            if assertion.get("transform", "identity") not in ALLOWED_TRANSFORMS:
                raise ValueError(f"{case_id}/{assertion_id}: invalid transform")


def _valid_path(path: Any) -> bool:
    return isinstance(path, str) and bool(path) and all(
        _PATH_PART.fullmatch(part) for part in path.split(".")
    )
