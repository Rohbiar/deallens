"""Build canonical semantic predictions from a persisted DealLens run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deallens.semantic_predictions import build_semantic_predictions  # noqa: E402


DESCRIPTOR_SCHEMA_VERSION = "semantic-case-descriptors/v1"
DEFAULT_DESCRIPTORS = Path(__file__).with_name("semantic_case_descriptors.json")


def load_descriptor_catalog(path: Path) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if _contains_key(catalog, "expected"):
        raise ValueError("descriptors must not contain expected values")
    if catalog.get("schema_version") != DESCRIPTOR_SCHEMA_VERSION:
        raise ValueError("unsupported semantic case descriptor schema")
    mappings = catalog.get("dimension_mappings")
    cases = catalog.get("cases")
    if not isinstance(mappings, dict) or not isinstance(cases, list) or not cases:
        raise ValueError("descriptor catalog requires mappings and cases")
    case_ids = set()
    for case in cases:
        case_id = case.get("case_id")
        if not isinstance(case_id, str) or not case_id or case_id in case_ids:
            raise ValueError(f"invalid or duplicate descriptor case_id: {case_id!r}")
        case_ids.add(case_id)
        if not isinstance(case.get("assertions"), list):
            raise ValueError(f"{case_id}: assertions must be a list")
        for assertion in case["assertions"]:
            dimension = assertion.get("dimension")
            if dimension not in mappings:
                raise ValueError(f"{case_id}: unmapped dimension {dimension!r}")
    return catalog


def _contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False


def expand_descriptors(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand compact external descriptors for the generic production adapter."""
    mappings = catalog["dimension_mappings"]
    expanded = []
    for case in catalog["cases"]:
        assertions = []
        for assertion in case["assertions"]:
            mapping = mappings[assertion["dimension"]]
            assertions.append({
                "assertion_id": assertion["assertion_id"],
                "dimension": assertion["dimension"],
                "statement_selector": dict(case.get("statement_selector", {})),
                "source_path": mapping["source_path"],
                "transform": mapping.get("transform", "identity"),
            })
        expanded.append({
            "case_id": case["case_id"],
            "document_id": case["document_id"],
            "document_layer": case.get("document_layer"),
            "field_name": case["field_name"],
            "assertions": assertions,
        })
    return expanded


def resolve_run_root(path: Path) -> Path:
    path = path.resolve()
    candidates = [path, path / "outputs"]
    for candidate in candidates:
        if (candidate / "manifest.json").is_file():
            return candidate
        latest = candidate / "latest.json"
        if latest.is_file():
            run_id = json.loads(latest.read_text(encoding="utf-8")).get("run_id")
            if not isinstance(run_id, str) or not run_id or Path(run_id).name != run_id:
                raise ValueError("invalid latest run identifier")
            run_root = candidate / run_id
            if not (run_root / "manifest.json").is_file():
                raise ValueError(f"latest run manifest not found: {run_root}")
            return run_root
    raise ValueError(f"run manifest or outputs/latest.json not found under {path}")


def load_structured_terms(path: Path) -> list[dict[str, Any]]:
    run_root = resolve_run_root(path)
    manifest = json.loads((run_root / "manifest.json").read_text(encoding="utf-8"))
    documents = manifest.get("documents")
    if not isinstance(documents, list) or not documents:
        raise ValueError("run manifest contains no documents")
    terms = []
    seen_documents = set()
    for document in documents:
        document_id = document.get("document_id")
        if (not isinstance(document_id, str) or not document_id
                or Path(document_id).name != document_id or document_id in seen_documents):
            raise ValueError(f"invalid or duplicate document_id: {document_id!r}")
        seen_documents.add(document_id)
        term_path = run_root / document_id / "structured_terms.json"
        if not term_path.is_file():
            raise ValueError(f"structured terms not found: {term_path}")
        document_terms = json.loads(term_path.read_text(encoding="utf-8"))
        if not isinstance(document_terms, list):
            raise ValueError(f"structured terms must be a list: {term_path}")
        if any(term.get("document_id") != document_id for term in document_terms):
            raise ValueError(f"structured term document mismatch: {term_path}")
        terms.extend(document_terms)
    return terms


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_root", type=Path,
                        help="run directory, outputs directory, or project root")
    parser.add_argument("--descriptors", type=Path, default=DEFAULT_DESCRIPTORS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    catalog = load_descriptor_catalog(args.descriptors)
    terms = load_structured_terms(args.run_root)
    predictions = build_semantic_predictions(terms, expand_descriptors(catalog))
    args.output.write_text(
        json.dumps(predictions, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "cases": len(predictions["cases"]),
        "output": str(args.output),
        "statuses": {
            status: sum(case["status"] == status for case in predictions["cases"])
            for status in ("supported", "unresolved", "abstention")
        },
        "terms": len(terms),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
