import copy
import json
import unittest
from pathlib import Path

from tests.evaluate_semantics import evaluate, load_reference, validate_reference


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = ROOT / "tests" / "semantic_reference.json"


def perfect_predictions(reference):
    cases = []
    for case in reference["cases"]:
        if case["expected_outcome"] == "unresolved":
            cases.append({"case_id": case["case_id"], "status": "unresolved", "assertions": []})
        else:
            cases.append(
                {
                    "case_id": case["case_id"],
                    "status": "supported",
                    "assertions": [
                        {"assertion_id": item["assertion_id"], "value": copy.deepcopy(item["expected"])}
                        for item in case["assertions"]
                    ],
                }
            )
    return {"schema_version": "1.0", "cases": cases}


def prediction_assertion(predictions, case_id, assertion_id):
    case = next(item for item in predictions["cases"] if item["case_id"] == case_id)
    return next(item for item in case["assertions"] if item["assertion_id"] == assertion_id)


class SemanticReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = load_reference(REFERENCE_PATH)

    def test_reference_schema_hashes_and_physical_page_excerpts(self):
        inventory = validate_reference(self.reference, ROOT)
        self.assertEqual(inventory["supported_cases"], 12)
        self.assertGreaterEqual(inventory["unresolved_cases"], 4)
        self.assertEqual(inventory["supported_assertions"], 72)

    def test_reference_is_valid_json_with_disclosed_non_gold_status(self):
        reloaded = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(reloaded["curation_status"], "agent_curated_not_human_gold")
        self.assertIn("not contract-wide", reloaded["scope"])


class SemanticEvaluatorMutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = load_reference(REFERENCE_PATH)

    def setUp(self):
        self.predictions = perfect_predictions(self.reference)

    def test_perfect_bounded_predictions_have_explicit_finite_denominators(self):
        report = evaluate(self.reference, self.predictions)
        metrics = report["metrics"]
        self.assertEqual(metrics["bounded_supported_assertion_denominator"], 72)
        self.assertEqual(metrics["bounded_asserted_prediction_denominator"], 72)
        self.assertEqual(metrics["bounded_atomic_precision"], 1.0)
        self.assertEqual(metrics["bounded_atomic_recall"], 1.0)
        self.assertEqual(metrics["counts"], {"correct": 72, "incorrect": 0, "omission": 0, "abstention": 0, "unresolved": 0})
        self.assertEqual(metrics["unresolved_reference_counts"]["respected"], 4)

    def test_wrong_actor_is_incorrect(self):
        assertion = prediction_assertion(
            self.predictions, "uber_remedy_limit", "uber_remedy_actor"
        )
        assertion["value"] = "Delivery Hero"
        counts = evaluate(self.reference, self.predictions)["metrics"]["counts"]
        self.assertEqual(counts["incorrect"], 1)

    def test_flipped_modality_is_incorrect(self):
        assertion = prediction_assertion(
            self.predictions, "organon_outside_date_extension", "organon_extension_obligation"
        )
        assertion["value"] = "automatic"
        counts = evaluate(self.reference, self.predictions)["metrics"]["counts"]
        self.assertEqual(counts["incorrect"], 1)

    def test_wrong_tail_period_is_incorrect(self):
        assertion = prediction_assertion(
            self.predictions, "organon_company_fee_tail", "organon_fee_timing"
        )
        assertion["value"]["amount"] = 12
        counts = evaluate(self.reference, self.predictions)["metrics"]["counts"]
        self.assertEqual(counts["incorrect"], 1)

    def test_missing_qualifier_is_incorrect_not_a_match(self):
        assertion = prediction_assertion(
            self.predictions, "uber_award_settlement_efforts", "uber_award_scope"
        )
        del assertion["value"]["target_performance_only_if"]
        counts = evaluate(self.reference, self.predictions)["metrics"]["counts"]
        self.assertEqual(counts["incorrect"], 1)

    def test_omission_abstention_and_unresolved_are_separate(self):
        self.predictions["cases"] = [
            case for case in self.predictions["cases"] if case["case_id"] != "bio_psu_treatment"
        ]
        next(case for case in self.predictions["cases"] if case["case_id"] == "organon_company_fee_tail")["status"] = "abstention"
        next(case for case in self.predictions["cases"] if case["case_id"] == "uber_remedy_limit")["status"] = "unresolved"
        counts = evaluate(self.reference, self.predictions)["metrics"]["counts"]
        self.assertEqual(counts["omission"], 6)
        self.assertEqual(counts["abstention"], 6)
        self.assertEqual(counts["unresolved"], 6)
        self.assertEqual(counts["incorrect"], 0)

    def test_forcing_a_redacted_reference_to_supported_is_incorrect(self):
        case = next(
            item for item in self.predictions["cases"] if item["case_id"] == "uber_bridge_fee_amounts_redacted"
        )
        case.update(status="supported", assertions=[{"assertion_id": "invented", "value": 0.25}])
        unresolved = evaluate(self.reference, self.predictions)["metrics"]["unresolved_reference_counts"]
        self.assertEqual(unresolved["incorrectly_resolved"], 1)
        self.assertEqual(unresolved["respected"], 3)


if __name__ == "__main__":
    unittest.main()
