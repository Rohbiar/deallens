"""Bounded evaluator for the agent-curated semantic reference set.

This module deliberately does not import DealLens extraction code.  Integrators must
adapt structured-term output to the small prediction contract documented in
docs/WORK_PACKAGE_D.md, which keeps the challenge set independent of implementation
choices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ALLOWED_DIMENSIONS = {"actor", "obligation", "trigger", "exception", "timing", "scope"}
PREDICTION_STATUSES = {"supported", "abstention", "unresolved"}


def _normalized_text(value: str) -> str:
    return " ".join(value.split())


def load_reference(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_reference(reference: dict[str, Any], root: Path | None = None) -> dict[str, int]:
    """Validate the frozen schema and, optionally, its PDF hashes/excerpts."""
    if reference.get("schema_version") != "1.0":
        raise ValueError("unsupported semantic reference schema")
    if reference.get("curation_status") != "agent_curated_not_human_gold":
        raise ValueError("reference set must disclose agent-curated status")

    cases = reference.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("reference cases must be a non-empty list")
    case_ids: set[str] = set()
    assertion_count = 0
    unresolved_count = 0
    pdf_cache: dict[Path, Any] = {}

    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            raise ValueError(f"invalid or duplicate case_id: {case_id!r}")
        case_ids.add(case_id)
        outcome = case.get("expected_outcome")
        if outcome not in {"supported", "unresolved"}:
            raise ValueError(f"{case_id}: invalid expected_outcome")

        source = case.get("source", {})
        pages = source.get("physical_pages")
        excerpts = source.get("excerpts")
        if not isinstance(pages, list) or not pages or not all(isinstance(p, int) and p > 0 for p in pages):
            raise ValueError(f"{case_id}: physical_pages must contain positive integers")
        if not isinstance(excerpts, list) or not excerpts:
            raise ValueError(f"{case_id}: at least one reproducible excerpt is required")
        for excerpt in excerpts:
            if excerpt.get("physical_page") not in pages or not _normalized_text(excerpt.get("text", "")):
                raise ValueError(f"{case_id}: excerpt page/text is invalid")

        assertions = case.get("assertions", [])
        if outcome == "supported":
            ids: set[str] = set()
            dimensions: set[str] = set()
            for assertion in assertions:
                assertion_id = assertion.get("assertion_id")
                dimension = assertion.get("dimension")
                if not isinstance(assertion_id, str) or not assertion_id or assertion_id in ids:
                    raise ValueError(f"{case_id}: invalid or duplicate assertion_id")
                if dimension not in ALLOWED_DIMENSIONS:
                    raise ValueError(f"{case_id}/{assertion_id}: invalid dimension")
                if "expected" not in assertion:
                    raise ValueError(f"{case_id}/{assertion_id}: expected value is required")
                ids.add(assertion_id)
                dimensions.add(dimension)
            missing = ALLOWED_DIMENSIONS - dimensions
            if missing:
                raise ValueError(f"{case_id}: missing atomic dimensions {sorted(missing)}")
            assertion_count += len(assertions)
        else:
            unresolved_count += 1
            if assertions:
                raise ValueError(f"{case_id}: unresolved references must not assert a resolved answer")
            if not case.get("unresolved_reason"):
                raise ValueError(f"{case_id}: unresolved_reason is required")

        if root is not None:
            pdf_path = root / source["file"]
            digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()
            if digest != source.get("sha256"):
                raise ValueError(f"{case_id}: source PDF hash mismatch")
            try:
                import fitz
            except ImportError as exc:  # pragma: no cover - dependency is pinned by the project
                raise RuntimeError("PyMuPDF is required for source excerpt validation") from exc
            if pdf_path not in pdf_cache:
                pdf_cache[pdf_path] = fitz.open(pdf_path)
            document = pdf_cache[pdf_path]
            for excerpt in excerpts:
                page_number = excerpt["physical_page"]
                if page_number > len(document):
                    raise ValueError(f"{case_id}: physical page is outside the PDF")
                page_text = _normalized_text(document[page_number - 1].get_text())
                if _normalized_text(excerpt["text"]) not in page_text:
                    raise ValueError(f"{case_id}: excerpt not found on physical page {page_number}")

    return {
        "cases": len(cases),
        "supported_cases": len(cases) - unresolved_count,
        "unresolved_cases": unresolved_count,
        "supported_assertions": assertion_count,
    }


def _prediction_map(predictions: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if predictions.get("schema_version") != "1.0":
        raise ValueError("unsupported semantic prediction schema")
    raw_cases = predictions.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError("predictions must contain a cases list")
    result: dict[str, dict[str, Any]] = {}
    for case in raw_cases:
        case_id = case.get("case_id")
        status = case.get("status")
        if not isinstance(case_id, str) or not case_id or case_id in result:
            raise ValueError(f"invalid or duplicate prediction case_id: {case_id!r}")
        if status not in PREDICTION_STATUSES:
            raise ValueError(f"{case_id}: invalid prediction status")
        assertions = case.get("assertions", [])
        if status == "supported" and not isinstance(assertions, list):
            raise ValueError(f"{case_id}: supported prediction assertions must be a list")
        result[case_id] = case
    return result


def evaluate(reference: dict[str, Any], predictions: dict[str, Any]) -> dict[str, Any]:
    """Score predictions with mutually exclusive atomic outcomes.

    Every supported reference assertion contributes exactly once to one of:
    correct, incorrect, omission, abstention, or unresolved.  Reference cases
    intentionally marked unresolved are reported separately and never enter the
    supported-assertion precision/recall denominator.
    """
    inventory = validate_reference(reference)
    predicted = _prediction_map(predictions)
    reference_ids = {case["case_id"] for case in reference["cases"]}
    totals = {key: 0 for key in ("correct", "incorrect", "omission", "abstention", "unresolved")}
    unresolved_reference = {
        key: 0 for key in ("respected", "incorrectly_resolved", "omission", "abstention")
    }
    case_results: list[dict[str, Any]] = []

    for case in reference["cases"]:
        case_id = case["case_id"]
        prediction = predicted.get(case_id)
        if case["expected_outcome"] == "unresolved":
            if prediction is None:
                category = "omission"
            elif prediction["status"] == "unresolved":
                category = "respected"
            elif prediction["status"] == "abstention":
                category = "abstention"
            else:
                category = "incorrectly_resolved"
            unresolved_reference[category] += 1
            case_results.append({"case_id": case_id, "reference_outcome": "unresolved", "category": category})
            continue

        assertion_results: list[dict[str, str]] = []
        if prediction is None:
            for expected in case["assertions"]:
                totals["omission"] += 1
                assertion_results.append({"assertion_id": expected["assertion_id"], "category": "omission"})
        elif prediction["status"] in {"abstention", "unresolved"}:
            category = prediction["status"]
            for expected in case["assertions"]:
                totals[category] += 1
                assertion_results.append({"assertion_id": expected["assertion_id"], "category": category})
        else:
            supplied: dict[str, Any] = {}
            expected_ids = {item["assertion_id"] for item in case["assertions"]}
            for assertion in prediction.get("assertions", []):
                assertion_id = assertion.get("assertion_id")
                if not isinstance(assertion_id, str) or not assertion_id or assertion_id in supplied:
                    raise ValueError(f"{case_id}: invalid or duplicate predicted assertion_id")
                if "value" not in assertion:
                    raise ValueError(f"{case_id}/{assertion_id}: predicted value is required")
                supplied[assertion_id] = assertion["value"]
            unknown_ids = set(supplied) - expected_ids
            if unknown_ids:
                raise ValueError(f"{case_id}: unknown predicted assertion_ids {sorted(unknown_ids)}")
            for expected in case["assertions"]:
                assertion_id = expected["assertion_id"]
                if assertion_id not in supplied:
                    category = "omission"
                elif supplied[assertion_id] == expected["expected"]:
                    category = "correct"
                else:
                    category = "incorrect"
                totals[category] += 1
                assertion_results.append({"assertion_id": assertion_id, "category": category})
        case_results.append(
            {"case_id": case_id, "reference_outcome": "supported", "assertions": assertion_results}
        )

    denominator = inventory["supported_assertions"]
    asserted_denominator = totals["correct"] + totals["incorrect"]
    if sum(totals.values()) != denominator:
        raise AssertionError("supported assertion accounting is not finite and exhaustive")
    metrics = {
        "bounded_supported_assertion_denominator": denominator,
        "bounded_asserted_prediction_denominator": asserted_denominator,
        "bounded_atomic_precision": (
            totals["correct"] / asserted_denominator if asserted_denominator else None
        ),
        "bounded_atomic_recall": totals["correct"] / denominator if denominator else None,
        "counts": totals,
        "unresolved_reference_case_denominator": inventory["unresolved_cases"],
        "unresolved_reference_counts": unresolved_reference,
        "out_of_scope_prediction_case_ids": sorted(set(predicted) - reference_ids),
    }
    return {
        "reference_set_id": reference["reference_set_id"],
        "scope": reference["scope"],
        "curation_status": reference["curation_status"],
        "metrics": metrics,
        "case_results": case_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("predictions", type=Path, help="canonical semantic predictions JSON")
    parser.add_argument(
        "--reference",
        type=Path,
        default=Path(__file__).with_name("semantic_reference.json"),
    )
    parser.add_argument("--output", type=Path, help="optional report path")
    parser.add_argument("--no-fail", action="store_true", help="do not fail on incorrect/omitted answers")
    args = parser.parse_args()
    reference = load_reference(args.reference)
    validate_reference(reference, Path(__file__).resolve().parents[1])
    predictions = json.loads(args.predictions.read_text(encoding="utf-8"))
    report = evaluate(reference, predictions)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    counts = report["metrics"]["counts"]
    unresolved = report["metrics"]["unresolved_reference_counts"]
    if not args.no_fail and (
        counts["incorrect"]
        or counts["omission"]
        or counts["abstention"]
        or counts["unresolved"]
        or unresolved["incorrectly_resolved"]
        or unresolved["omission"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
