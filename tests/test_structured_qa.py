import copy
import unittest
from pathlib import Path

from deallens.qa import UNSUPPORTED, answer
from deallens.risk import risk_map
from deallens.structured_terms import (condition, evidence_ref, party, statement,
                                       term_record, timing, unresolved)
from deallens.term_comparison import compare_structured_terms
from deallens.term_timeline import structured_term_timeline


ROOT = Path(__file__).resolve().parents[1]


def context(layer="transaction-agreement"):
    section_id = f"{layer}:8.01:1"
    return {
        "schema_version": "retrieval-context/v1", "source_hash": "synthetic-hash",
        "document_id": "synthetic", "root_section_ids": [section_id],
        "section_ids": [section_id],
        "sections": [{"section_id": section_id, "document_layer": layer}],
        "sources": [{"source_id": f"src-{layer}", "section_id": section_id,
                     "evidence": "Synthetic fixture only"}],
        "unresolved": [], "budget": {"truncated": False},
    }


def extension(actor="Parent", layer="transaction-agreement", status="machine_supported",
              unresolved_items=()):
    source = evidence_ref(f"src-{layer}")
    stmt = statement(
        "extension", party(actor, actor.lower()),
        {"modality": "permitted", "verb": "extend", "object": "outside date"},
        statement_id=f"extension-{layer}",
        conditions=[condition("regulatory-open", "Regulatory condition remains open",
                              evidence=[source])],
        timing_value=timing(clock_type="relative", value=90, unit="calendar_days",
                            anchor="initial outside date", evidence=[source]),
        evidence=[source],
    )
    return term_record("extension_dates_and_conditions", context(layer), [stmt],
                       status=status, unresolved_items=unresolved_items)


def award_term(status="machine_supported", open_dependency=True):
    source = evidence_ref("src-transaction-agreement")
    stmt = statement(
        "award_treatment", party("Company", "company"),
        {"modality": "required", "verb": "cash_out", "object": "pre-2026 awards"},
        statement_id="award-cohort-1", conditions=[condition(
            "grant-cohort", "Award was granted before 2026", evidence=[source])],
        evidence=[source])
    items = ([unresolved("missing_schedule", "post-2026 award schedule",
                         materiality="material", evidence=[source])]
             if open_dependency else [])
    return term_record("award_cohort_differences", context(), [stmt], status=status,
                       unresolved_items=items)


class StructuredConsumerTests(unittest.TestCase):
    def test_actor_dependent_extensions_are_not_a_match(self):
        summary = extension("Company", "8-k-summary")
        agreement = extension("Parent", "transaction-agreement")
        row = compare_structured_terms([summary, agreement])[0]
        self.assertEqual(row["classification"], "conflict")
        self.assertIn("actor", {item["component"] for item in row["differences"]})

    def test_uncertainty_is_never_a_match(self):
        summary = extension("Parent", "8-k-summary", status="candidate")
        agreement = extension("Parent", "transaction-agreement")
        self.assertEqual(compare_structured_terms([summary, agreement])[0]["classification"],
                         "unresolved")

    def test_timeline_retains_actor_election_condition_and_nonoccurrence(self):
        event = structured_term_timeline([extension()])[0]
        self.assertEqual(event["actor"]["role"], "parent")
        self.assertTrue(event["election_required"])
        self.assertEqual(event["conditions"][0]["condition_id"], "regulatory-open")
        self.assertEqual(event["occurrence_status"], "not_established")
        self.assertIsNone(event["contractual_date"])

    def test_partial_award_cohort_separates_supported_and_unresolved(self):
        result = answer("awards", [], [], structured_terms=[award_term()])
        self.assertEqual(result["status"], "partial")
        self.assertTrue(result["supported_components"])
        self.assertTrue(result["unresolved_components"])
        self.assertIn("award_cohort_differences", result["missing_fields"])

    def test_candidate_only_retains_exact_unsupported_wording(self):
        result = answer("extensions", [], [], structured_terms=[extension(status="candidate")])
        self.assertEqual(result["answer"], UNSUPPORTED)
        self.assertEqual(result["status"], "requires_review")
        self.assertTrue(result["unresolved_components"])

    def test_strict_mode_excludes_machine_supported_components(self):
        result = answer("extensions", [], [], strict=True,
                        structured_terms=[extension(status="machine_supported")])
        self.assertEqual(result["answer"], UNSUPPORTED)
        self.assertEqual(result["unresolved_components"][0]["reason"],
                         "strict_mode_exclusion")

    def test_conflicting_prices_still_block_legacy_answer(self):
        records = []
        for layer, value in [("8-k-summary", 10), ("transaction-agreement", 11)]:
            records.append({"field_name": "consideration_per_share", "document_layer": layer,
                            "status": "supported", "normalized_value": value,
                            "currency": "USD", "evidence": str(value),
                            "review_status": "unreviewed"})
        comparisons = [{"field_name": "consideration_per_share",
                        "classification": "conflict"}]
        result = answer("consideration", records, comparisons)
        self.assertEqual(result["answer"], UNSUPPORTED)
        self.assertEqual(result["status"], "conflict")

    def test_risk_map_exposes_supported_and_unresolved_separately(self):
        row = next(item for item in risk_map([], [award_term()])
                   if item["field"] == "award_cohort_differences")
        self.assertEqual(row["source_status"], "partial")
        self.assertTrue(row["supported_components"])
        self.assertTrue(row["unresolved_components"])

    def test_all_required_questions_fail_closed_without_evidence(self):
        # Three synthetic transactions x twelve categories exercises the 36-answer gate.
        from deallens.catalog import QUESTIONS
        for _document in range(3):
            for question in QUESTIONS:
                self.assertEqual(answer(question, [], [])["answer"], UNSUPPORTED)

    def test_ui_escapes_answers_and_structured_source_text(self):
        ui = (ROOT / "deallens/ui.html").read_text()
        self.assertIn("${esc(a.answer)}", ui)
        self.assertIn("${esc(x.text||x.expression||x.reason)}", ui)
        self.assertIn("${esc(a.name||a.role)}", ui)
        self.assertNotIn("<h3>${a.answer}</h3>", ui)


if __name__ == "__main__":
    unittest.main()
