import copy
import inspect
import json
import unittest
from pathlib import Path

from deallens.ingest import ingest
from deallens.provisions import provision_records
from deallens.structured_terms import (INTERPRETED_FIELDS, condition, evidence_ref, interpret_term,
                                       party, statement, term_record, timing,
                                       unresolved)
import deallens.structured_terms as structured_terms
from deallens.term_validation import validate_term


def context():
    return {
        "schema_version": "retrieval-context/v1",
        "source_hash": "abc123",
        "document_id": "synthetic",
        "root_section_ids": ["transaction-agreement:8.01:1"],
        "section_ids": ["transaction-agreement:8.01:1"],
        "sections": [{"section_id": "transaction-agreement:8.01:1",
                      "document_layer": "transaction-agreement"}],
        "sources": [{"source_id": "src-1", "section_id": "transaction-agreement:8.01:1",
                     "locator": "synthetic:abc123:p1:chars0-100", "evidence": "Synthetic clause"}],
        "unresolved": [],
        "budget": {"truncated": False},
    }


def extension_term():
    source = evidence_ref("src-1")
    stmt = statement(
        "extension", party("Parent", "parent"),
        {"modality": "permitted", "verb": "extend", "object": "outside date"},
        statement_id="extension-1",
        conditions=[condition("condition-regulatory", "Regulatory condition remains unsatisfied", evidence=[source])],
        exceptions=[condition("exception-breach", "Electing party is not in material breach", evidence=[source])],
        timing_value=timing(clock_type="relative", value=90, unit="calendar_days",
                            anchor="initial outside date", evidence=[source]),
        evidence=[source],
    )
    return term_record("extension_dates_and_conditions", context(), [stmt],
                       validation_basis=["independent_atomic_assertions"])


def assertion():
    return {"statement_id": "extension-1",
            "actor": {"role": "parent"},
            "action": {"modality": "permitted", "verb": "extend", "object": "outside date"},
            "timing": {"unit": "calendar_days", "anchor": "initial outside date"},
            "required_condition_ids": ["condition-regulatory"],
            "required_exception_ids": ["exception-breach"]}


class StructuredTermTests(unittest.TestCase):
    def test_schema_preserves_actor_conditions_exception_timing_and_evidence(self):
        term = extension_term()
        result = validate_term(term, context(), [assertion()])
        self.assertTrue(result["valid"])
        self.assertTrue(result["machine_support_eligible"])
        self.assertEqual(term["review_status"], "unreviewed")

    def test_changed_actor_is_detected(self):
        term = extension_term(); term["statements"][0]["actor"]["role"] = "company"
        result = validate_term(term, context(), [assertion()])
        self.assertIn("assertion extension-1: actor.role mismatch", result["errors"])

    def test_omitted_exception_is_detected(self):
        term = extension_term(); term["statements"][0]["exceptions"] = []
        result = validate_term(term, context(), [assertion()])
        self.assertIn("assertion extension-1: exceptions omitted", result["errors"])

    def test_wrong_time_unit_is_detected(self):
        term = extension_term(); term["statements"][0]["timing"]["unit"] = "business_days"
        result = validate_term(term, context(), [assertion()])
        self.assertIn("assertion extension-1: timing.unit mismatch", result["errors"])

    def test_contradictory_modalities_are_detected(self):
        term = extension_term(); opposite = copy.deepcopy(term["statements"][0])
        opposite["statement_id"] = "extension-2"
        opposite["action"]["modality"] = "prohibited"
        term["statements"].append(opposite)
        result = validate_term(term, context(), [assertion()])
        self.assertIn("statements: contradictory modalities for same atomic assertion", result["errors"])

    def test_unresolved_context_blocks_support(self):
        ctx = context(); ctx["unresolved"] = [{"reason": "missing_target"}]
        term = extension_term()
        result = validate_term(term, ctx, [assertion()])
        self.assertTrue(result["valid"])
        self.assertFalse(result["machine_support_eligible"])
        self.assertIn("retrieval_context_unresolved", result["warnings"])

    def test_material_unresolved_interpretation_blocks_support(self):
        term = extension_term()
        term["unresolved"] = [unresolved("missing_definition", "Burdensome Condition",
                                         materiality="material", evidence=[evidence_ref("src-1")])]
        result = validate_term(term, context(), [assertion()])
        self.assertFalse(result["machine_support_eligible"])

    def test_statement_level_material_unresolved_blocks_support(self):
        term = extension_term()
        term["statements"][0]["unresolved"] = [unresolved(
            "missing_exception", "referenced proviso", materiality="material",
            evidence=[evidence_ref("src-1")])]
        result = validate_term(term, context(), [assertion()])
        self.assertTrue(result["valid"])
        self.assertFalse(result["machine_support_eligible"])
        self.assertIn("material_interpretation_unresolved", result["warnings"])

    def test_unknown_evidence_and_self_verification_fail_closed(self):
        term = extension_term()
        term["statements"][0]["evidence"] = [evidence_ref("invented")]
        term["review_status"] = "verified"
        result = validate_term(term, context(), [assertion()])
        self.assertFalse(result["valid"])
        self.assertTrue(any("unknown source_id" in error for error in result["errors"]))
        self.assertIn("review_status: cannot self-verify", result["errors"])

    def test_shape_without_independent_assertions_never_establishes_support(self):
        result = validate_term(extension_term(), context())
        self.assertTrue(result["valid"])
        self.assertFalse(result["machine_support_eligible"])
        self.assertIn("semantic_support_not_evaluated", result["warnings"])

    def test_no_recognized_statement_is_valid_materially_unresolved_record(self):
        ctx = context()
        ctx["sources"][0]["evidence"] = "No recognized operative grammar appears here."
        term = interpret_term("remedy_limitations", ctx)
        result = validate_term(term, ctx)
        self.assertEqual(term["status"], "unresolved")
        self.assertEqual(term["statements"], [])
        self.assertTrue(result["valid"], result["errors"])
        self.assertFalse(result["machine_support_eligible"])
        self.assertEqual(term["unresolved"][-1]["reason"], "no_recognized_atomic_statement")

    def test_automatic_extension_cannot_be_changed_to_party_election(self):
        term = extension_term()
        term["statements"][0]["action"]["modality"] = "automatic"
        result = validate_term(term, context(), [assertion()])
        self.assertIn(
            "statements[0].actor.role: automatic extension cannot be a party election",
            result["errors"],
        )

    def test_fee_tail_requires_payee_trigger_and_months_after_termination(self):
        source = evidence_ref("src-1")
        tail = statement(
            "fee_tail", party("Company", "company"),
            {"modality": "required", "verb": "pay", "object": "termination fee"},
            beneficiary=party("Parent", "payee"),
            trigger={"event": "subsequent transaction completed", "evidence": [source]},
            timing_value=timing(clock_type="relative", value=12, unit="months",
                                anchor="termination", evidence=[source]),
            evidence=[source],
        )
        term = term_record("fee_triggers_and_tails", context(), [tail])
        self.assertTrue(validate_term(term, context())["valid"])
        term["statements"][0]["timing"]["unit"] = "business_days"
        result = validate_term(term, context())
        self.assertIn(
            "statements[0].timing: fee tail requires months after termination",
            result["errors"],
        )

    def test_fee_payee_mutation_is_detected_by_atomic_assertion(self):
        source = evidence_ref("src-1")
        fee = statement(
            "fee_trigger", party("Company", "company"),
            {"modality": "required", "verb": "pay", "object": "termination fee"},
            beneficiary=party("Parent", "payee"),
            trigger={"event": "agreement terminated", "evidence": [source]},
            evidence=[source], statement_id="fee-1",
        )
        term = term_record("fee_triggers_and_tails", context(), [fee],
                           validation_basis=["independent_atomic_assertions"])
        expected = {"statement_id": "fee-1", "beneficiary": {"name": "Parent"}}
        self.assertTrue(validate_term(term, context(), [expected])["machine_support_eligible"])
        term["statements"][0]["beneficiary"]["name"] = "Company"
        self.assertIn("assertion fee-1: beneficiary.name mismatch",
                      validate_term(term, context(), [expected])["errors"])


class SourceBackedB2Tests(unittest.TestCase):
    def test_generic_interpreter_contains_no_transaction_names(self):
        production_source = inspect.getsource(structured_terms)
        self.assertNotIn("Uber", production_source)
        self.assertNotIn("Delivery Hero", production_source)
        self.assertNotIn("Bio-Techne", production_source)
        self.assertNotIn("Organon", production_source)

    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.terms = {}
        for config in json.loads((root / "config/sources.json").read_text()):
            document = ingest(root / "data/sources" / f"{config['document_id']}.pdf", config)
            records = provision_records(document, "structured-b2-test")
            cls.terms[config["document_id"]] = {}
            for field in ("extension_dates_and_conditions", "fee_triggers_and_tails"):
                bundle = next(row for row in records if row["field_name"] == field)["context_bundle"]
                term = interpret_term(field, bundle)
                cls.terms[config["document_id"]][field] = (term, bundle)

    def test_extension_modes_actors_conditions_and_caps_across_sources(self):
        bio, _ = self.terms["bio_techne"]["extension_dates_and_conditions"]
        automatic = [s for s in bio["statements"] if s["action"]["modality"] == "automatic"]
        self.assertEqual(len(automatic), 2)
        self.assertTrue(all(s["conditions"] and s["actor"]["role"] == "automatic_mechanism"
                            for s in automatic))
        self.assertTrue(any(s["actor"]["role"] == "joint_parties" for s in bio["statements"]))

        organon, _ = self.terms["organon"]["extension_dates_and_conditions"]
        election = organon["statements"][0]
        self.assertEqual(election["actor"]["role"], "either_party")
        self.assertEqual(election["action"]["verb"], "elect to extend")
        self.assertTrue(any("written notice" in item["text"].lower()
                            for item in election["conditions"]))

        uber, _ = self.terms["uber_delivery_hero"]["extension_dates_and_conditions"]
        authorization = uber["statements"][0]
        self.assertEqual(authorization["actor"]["role"], "regulator")
        self.assertEqual(authorization["action"]["verb"], "authorize later date")
        self.assertTrue(authorization["exceptions"])

    def test_fee_payers_payees_deadlines_amounts_and_tails_across_sources(self):
        bio, _ = self.terms["bio_techne"]["fee_triggers_and_tails"]
        bio_tail = next(s for s in bio["statements"] if s["kind"] == "fee_tail")
        self.assertEqual((bio_tail["timing"]["value"], bio_tail["timing"]["unit"]),
                         (12, "months"))
        self.assertEqual(bio_tail["actor"]["role"], "company")

        organon, _ = self.terms["organon"]["fee_triggers_and_tails"]
        organon_tail = next(s for s in organon["statements"] if s["kind"] == "fee_tail")
        self.assertEqual((organon_tail["timing"]["value"], organon_tail["timing"]["anchor"]),
                         (9, "termination"))

        uber, _ = self.terms["uber_delivery_hero"]["fee_triggers_and_tails"]
        obligations = {(s["actor"]["name"], s["beneficiary"]["name"]): s
                       for s in uber["statements"]}
        self.assertEqual(obligations[("Delivery Hero", "Uber")]["amount"]["value"], 200_000_000)
        self.assertEqual(obligations[("Uber", "Delivery Hero")]["amount"]["value"], 700_000_000)
        self.assertTrue(all(s["timing"]["unit"] == "business_days" for s in uber["statements"]))

    def test_real_candidates_are_schema_valid_source_bound_and_not_support_eligible(self):
        for by_field in self.terms.values():
            for term, bundle in by_field.values():
                result = validate_term(term, bundle)
                self.assertTrue(result["valid"], result["errors"])
                self.assertFalse(result["machine_support_eligible"])
                known = {source["source_id"] for source in bundle["sources"]}
                for stmt in term["statements"]:
                    self.assertTrue({ref["source_id"] for ref in stmt["evidence"]}.issubset(known))
                self.assertTrue(term["unresolved"])


class SourceBackedB3B4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.documents = {}
        cls.terms = {}
        for config in json.loads((root / "config/sources.json").read_text()):
            document = ingest(root / "data/sources" / f"{config['document_id']}.pdf", config)
            cls.documents[config["document_id"]] = document
            cls.terms[config["document_id"]] = {}
            for record in provision_records(document, "structured-b34-test"):
                if record["field_name"] not in INTERPRETED_FIELDS:
                    continue
                bundle = record["context_bundle"]
                cls.terms[config["document_id"]][record["field_name"]] = (
                    interpret_term(record["field_name"], bundle), bundle)

    def test_remedy_modalities_actors_scopes_and_exceptions_across_sources(self):
        bio, _ = self.terms["bio_techne"]["remedy_limitations"]
        limit = next(s for s in bio["statements"] if s["action"]["modality"] == "prohibited")
        self.assertEqual(limit["actor"]["role"], "protected_parties")
        self.assertEqual(limit["business_scope"]["limit"], "Burdensome Condition")
        self.assertTrue(limit["exceptions"])

        organon, _ = self.terms["organon"]["remedy_limitations"]
        covenant = organon["statements"][0]
        self.assertEqual(covenant["action"]["modality"], "required")
        self.assertEqual(covenant["actor"]["role"], "joint_parties")
        self.assertEqual(covenant["business_scope"]["limit"], "Substantial Detriment")

        uber, _ = self.terms["uber_delivery_hero"]["remedy_limitations"]
        efforts = uber["statements"][0]
        self.assertEqual(efforts["actor"]["role"], "acquiror")
        self.assertEqual(efforts["action"]["verb"], "use best efforts to offer or accept remedy")
        self.assertTrue(efforts["exceptions"])

    def test_awards_preserve_performance_and_grant_cohorts(self):
        bio, _ = self.terms["bio_techne"]["award_cohort_differences"]
        measures = {(s["business_scope"]["award_type"],
                     s["business_scope"].get("performance_measurement"))
                    for s in bio["statements"]}
        self.assertIn(("PSU", "maximum"), measures)
        self.assertIn(("option", "target"), measures)

        organon, _ = self.terms["organon"]["award_cohort_differences"]
        cohorts = {(s["business_scope"]["award_type"], s["business_scope"]["cohort"]): s
                   for s in organon["statements"]}
        self.assertEqual(len(cohorts), 4)
        self.assertEqual(cohorts[("PSU", "pre_grant_year:2026")]["business_scope"]["performance_measurement"],
                         "target")
        self.assertTrue(cohorts[("PSU", "pre_grant_year:2026")]["unresolved"])

        uber, _ = self.terms["uber_delivery_hero"]["award_cohort_differences"]
        efforts = uber["statements"][0]
        self.assertEqual(efforts["action"]["modality"], "required")
        self.assertIn("actual", efforts["business_scope"]["performance_measurement"])
        self.assertTrue(efforts["unresolved"])

    def test_financing_separates_transaction_and_lender_conditions(self):
        organon, _ = self.terms["organon"]["financing_conditions"]
        closing = organon["statements"][0]
        self.assertEqual(closing["business_scope"]["condition_type"],
                         "transaction_closing_condition")
        self.assertEqual(closing["action"]["modality"], "prohibited")

        uber, _ = self.terms["uber_delivery_hero"]["financing_conditions"]
        types = {s["business_scope"]["condition_type"] for s in uber["statements"]}
        self.assertEqual(types, {"lender_funding_condition", "lender_certain_funds_restriction"})
        lender = [s for s in uber["statements"]
                  if s["business_scope"]["condition_type"] == "lender_funding_condition"]
        self.assertEqual({s["business_scope"]["funding_phase"] for s in lender},
                         {"initial_borrowing", "post_closing_borrowing"})
        self.assertTrue(all(s["conditions"] for s in lender))

    def test_b3_b4_candidates_are_valid_source_bound_and_fail_closed(self):
        for by_field in self.terms.values():
            for field in ("remedy_limitations", "award_cohort_differences", "financing_conditions"):
                if field not in by_field:
                    continue
                term, bundle = by_field[field]
                result = validate_term(term, bundle)
                self.assertTrue(result["valid"], (term["document_id"], field, result["errors"]))
                self.assertFalse(result["machine_support_eligible"])
                self.assertEqual(term["status"], "candidate")
                self.assertEqual(term["review_status"], "unreviewed")

    def test_remedy_actor_scope_and_exception_mutations_fail_validation(self):
        term, bundle = self.terms["bio_techne"]["remedy_limitations"]
        mutated = copy.deepcopy(term)
        mutated["statements"][0]["actor"]["role"] = ""
        mutated["statements"][0]["business_scope"] = {}
        mutated["statements"][0]["exceptions"] = []
        errors = validate_term(mutated, bundle)["errors"]
        self.assertTrue(any("actor" in error for error in errors))
        self.assertTrue(any("business_scope" in error for error in errors))
        self.assertTrue(any("exceptions" in error for error in errors))

    def test_award_cohort_and_lender_condition_mutations_fail_validation(self):
        award, award_bundle = self.terms["organon"]["award_cohort_differences"]
        mutated_award = copy.deepcopy(award)
        mutated_award["statements"][0]["business_scope"].pop("cohort")
        self.assertTrue(any("cohort" in error
                            for error in validate_term(mutated_award, award_bundle)["errors"]))

        financing, financing_bundle = self.terms["uber_delivery_hero"]["financing_conditions"]
        mutated_financing = copy.deepcopy(financing)
        lender = next(s for s in mutated_financing["statements"]
                      if s["business_scope"]["condition_type"] == "lender_funding_condition")
        lender["actor"]["role"] = "transaction_parties"
        lender["conditions"] = []
        errors = validate_term(mutated_financing, financing_bundle)["errors"]
        self.assertTrue(any("lender funding condition" in error for error in errors))
        self.assertTrue(any("lender funding conditions required" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
