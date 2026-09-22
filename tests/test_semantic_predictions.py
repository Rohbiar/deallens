import copy
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import deallens.semantic_predictions as semantic_predictions
from deallens.semantic_predictions import build_semantic_predictions
from tests.build_semantic_predictions import (expand_descriptors,
                                               load_descriptor_catalog)


ROOT = Path(__file__).resolve().parents[1]
DESCRIPTORS = ROOT / "tests" / "semantic_case_descriptors.json"


def supported_term():
    return {
        "schema_version": "structured-terms/v1",
        "document_id": "synthetic",
        "document_layer": "transaction-agreement",
        "field_name": "extension_dates_and_conditions",
        "status": "machine_supported",
        "review_status": "unreviewed",
        "unresolved": [],
        "statements": [{
            "statement_id": "extension-1",
            "kind": "extension",
            "actor": {"name": "Parent", "role": "parent"},
            "action": {"modality": "permitted", "verb": "extend", "object": "Outside Date"},
            "trigger": {"event": "regulatory condition remains unsatisfied"},
            "conditions": [{"text": "written notice before the initial date"}],
            "exceptions": [{"text": "electing party is not in material breach"}],
            "timing": {"clock_type": "relative", "value": 90,
                       "unit": "calendar_days", "anchor": "initial Outside Date"},
            "business_scope": {"date_type": "Outside Date"},
            "unresolved": [],
        }],
    }


def descriptor():
    selector = {"statement_id": "extension-1"}
    return {
        "case_id": "synthetic_extension",
        "document_id": "synthetic",
        "document_layer": "transaction-agreement",
        "field_name": "extension_dates_and_conditions",
        "assertions": [
            {"assertion_id": "actor", "dimension": "actor",
             "statement_selector": selector, "source_path": "actor.name"},
            {"assertion_id": "obligation", "dimension": "obligation",
             "statement_selector": selector, "source_path": "action"},
            {"assertion_id": "trigger", "dimension": "trigger",
             "statement_selector": selector, "source_path": "trigger.event"},
            {"assertion_id": "exception", "dimension": "exception",
             "statement_selector": selector, "source_path": "exceptions",
             "transform": "condition_texts"},
            {"assertion_id": "timing", "dimension": "timing",
             "statement_selector": selector, "source_path": "timing"},
            {"assertion_id": "scope", "dimension": "scope",
             "statement_selector": selector, "source_path": "business_scope"},
        ],
    }


def case(predictions):
    return predictions["cases"][0]


def assertion_value(predictions, assertion_id):
    return next(row["value"] for row in case(predictions)["assertions"]
                if row["assertion_id"] == assertion_id)


class SemanticPredictionAdapterTests(unittest.TestCase):
    def test_production_adapter_contains_no_transaction_or_frozen_case_answers(self):
        source = inspect.getsource(semantic_predictions)
        for hidden_value in ("Bio-Techne", "Organon", "Uber", "Delivery Hero",
                             "2027-03-25", "700000000", "Substantial Detriment"):
            self.assertNotIn(hidden_value, source)

    def test_clean_supported_term_maps_only_declared_generic_paths(self):
        predictions = build_semantic_predictions([supported_term()], [descriptor()])
        self.assertEqual(predictions["schema_version"], "1.0")
        self.assertEqual(case(predictions)["status"], "supported")
        self.assertEqual(assertion_value(predictions, "actor"), "Parent")
        self.assertEqual(assertion_value(predictions, "trigger"),
                         "regulatory condition remains unsatisfied")
        self.assertEqual(assertion_value(predictions, "exception"),
                         ["electing party is not in material breach"])
        self.assertEqual(assertion_value(predictions, "timing")["value"], 90)

    def test_actor_and_timing_mutations_flow_through_without_expected_answers(self):
        original = build_semantic_predictions([supported_term()], [descriptor()])
        mutated = supported_term()
        mutated["statements"][0]["actor"]["name"] = "Company"
        mutated["statements"][0]["timing"]["unit"] = "business_days"
        changed = build_semantic_predictions([mutated], [descriptor()])
        self.assertEqual(assertion_value(original, "actor"), "Parent")
        self.assertEqual(assertion_value(changed, "actor"), "Company")
        self.assertEqual(assertion_value(changed, "timing")["unit"], "business_days")

    def test_candidate_and_explicitly_unresolved_terms_cannot_assert(self):
        for status in ("candidate", "unresolved"):
            term = supported_term()
            term["status"] = status
            prediction = case(build_semantic_predictions([term], [descriptor()]))
            self.assertEqual(prediction, {
                "case_id": "synthetic_extension", "status": "unresolved", "assertions": []
            })

    def test_term_or_statement_material_uncertainty_blocks_entire_case(self):
        for location in ("term", "statement"):
            term = supported_term()
            item = {"reason": "missing schedule", "materiality": "material"}
            if location == "term":
                term["unresolved"] = [item]
            else:
                term["statements"][0]["unresolved"] = [item]
            self.assertEqual(
                case(build_semantic_predictions([term], [descriptor()]))["status"],
                "unresolved",
            )

    def test_unknown_materiality_fails_closed_but_non_material_does_not(self):
        term = supported_term()
        term["unresolved"] = [{"reason": "open", "materiality": "unknown"}]
        self.assertEqual(case(build_semantic_predictions([term], [descriptor()]))["status"],
                         "unresolved")
        term["unresolved"][0]["materiality"] = "non_material"
        self.assertEqual(case(build_semantic_predictions([term], [descriptor()]))["status"],
                         "supported")

    def test_ambiguous_statement_or_term_selection_is_unresolved(self):
        term = supported_term()
        duplicate = copy.deepcopy(term["statements"][0])
        term["statements"].append(duplicate)
        self.assertEqual(case(build_semantic_predictions([term], [descriptor()]))["status"],
                         "unresolved")
        self.assertEqual(case(build_semantic_predictions(
            [supported_term(), supported_term()], [descriptor()]))["status"], "unresolved")

    def test_absent_term_is_an_explicit_abstention(self):
        prediction = case(build_semantic_predictions([], [descriptor()]))
        self.assertEqual(prediction, {
            "case_id": "synthetic_extension", "status": "abstention", "assertions": []
        })

    def test_descriptor_without_assertion_mappings_cannot_resolve_a_case(self):
        unmapped = descriptor()
        unmapped["assertions"] = []
        self.assertEqual(case(build_semantic_predictions(
            [supported_term()], [unmapped]))["status"], "unresolved")

    def test_missing_path_or_invalid_descriptor_never_produces_support(self):
        missing = descriptor()
        missing["assertions"][0]["source_path"] = "actor.canonical_name"
        self.assertEqual(case(build_semantic_predictions(
            [supported_term()], [missing]))["status"], "unresolved")
        invalid = descriptor()
        invalid["assertions"][0]["source_path"] = "actor[0]"
        with self.assertRaisesRegex(ValueError, "invalid source_path"):
            build_semantic_predictions([supported_term()], [invalid])

    def test_duplicate_case_and_assertion_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate case_id"):
            build_semantic_predictions([supported_term()], [descriptor(), descriptor()])
        duplicate = descriptor()
        duplicate["assertions"][1]["assertion_id"] = "actor"
        with self.assertRaisesRegex(ValueError, "duplicate assertion_id"):
            build_semantic_predictions([supported_term()], [duplicate])


class SemanticPredictionBuilderTests(unittest.TestCase):
    def test_external_descriptor_catalog_is_valid_and_contains_no_answers(self):
        catalog = load_descriptor_catalog(DESCRIPTORS)
        self.assertEqual(len(catalog["cases"]), 16)
        self.assertNotIn('"expected"', DESCRIPTORS.read_text(encoding="utf-8"))
        expanded = expand_descriptors(catalog)
        self.assertEqual(len(expanded), 16)
        self.assertEqual(len({case["case_id"] for case in expanded}), 16)
        supported_mappings = [case for case in expanded if case["assertions"]]
        self.assertEqual(len(supported_mappings), 12)
        self.assertTrue(all(len(case["assertions"]) == 6
                            for case in supported_mappings))
        reference = json.loads((ROOT / "tests" / "semantic_reference.json").read_text())
        reference_inventory = {
            case["case_id"]: {(item["assertion_id"], item["dimension"])
                              for item in case["assertions"]}
            for case in reference["cases"]
        }
        descriptor_inventory = {
            case["case_id"]: {(item["assertion_id"], item["dimension"])
                              for item in case["assertions"]}
            for case in catalog["cases"]
        }
        self.assertEqual(descriptor_inventory, reference_inventory)

    def test_cli_builds_canonical_predictions_from_persisted_run_terms(self):
        catalog = load_descriptor_catalog(DESCRIPTORS)
        with tempfile.TemporaryDirectory() as temporary:
            run_root = Path(temporary) / "outputs" / "test-run"
            run_root.mkdir(parents=True)
            document_ids = sorted({case["document_id"] for case in catalog["cases"]})
            (run_root / "manifest.json").write_text(json.dumps({
                "run_id": "test-run",
                "documents": [{"document_id": document_id}
                              for document_id in document_ids],
            }), encoding="utf-8")
            for document_id in document_ids:
                document_root = run_root / document_id
                document_root.mkdir()
                fields = sorted({case["field_name"] for case in catalog["cases"]
                                 if case["document_id"] == document_id})
                terms = [{
                    "schema_version": "structured-terms/v1",
                    "document_id": document_id,
                    "document_layer": "transaction-agreement",
                    "field_name": field,
                    "status": "candidate",
                    "review_status": "unreviewed",
                    "statements": [],
                    "unresolved": [],
                } for field in fields]
                (document_root / "structured_terms.json").write_text(
                    json.dumps(terms), encoding="utf-8"
                )
            output = Path(temporary) / "predictions.json"
            completed = subprocess.run(
                [sys.executable, str(ROOT / "tests" / "build_semantic_predictions.py"),
                 str(run_root), "--output", str(output)],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            predictions = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(predictions["schema_version"], "1.0")
            self.assertEqual(len(predictions["cases"]), 16)
            self.assertEqual({case["status"] for case in predictions["cases"]},
                             {"unresolved"})
            self.assertIn('"cases": 16', completed.stdout)


if __name__ == "__main__":
    unittest.main()
