import copy
import json
import unittest
from pathlib import Path

from deallens.analytics import (map_structured_terms_to_scenario_inputs,
                                run_analytics)


ROOT = Path(__file__).resolve().parents[1]


def extension_term(statement_id, value, modality, *, status="machine_supported",
                   conditions=()):
    return {
        "term_id": f"term-{statement_id}",
        "field_name": "extension_dates_and_conditions",
        "status": status,
        "unresolved": [],
        "statements": [{
            "statement_id": statement_id,
            "actor": {"name": "Parent", "role": "parent"},
            "action": {"modality": modality, "verb": "extend",
                       "object": "outside date"},
            "conditions": list(conditions),
            "exceptions": [],
            "timing": {"clock_type": "fixed_date", "value": value,
                       "unit": "date", "anchor": "outside date"},
            "evidence": [{"source_id": f"source-{statement_id}"}],
        }],
    }


def financing_term():
    return {
        "term_id": "term-funding",
        "field_name": "financing_conditions",
        "status": "machine_supported",
        "unresolved": [],
        "statements": [
            {"statement_id": "lender-condition", "actor": {"name": "Lenders", "role": "lenders"},
             "action": {"modality": "conditional", "verb": "fund", "object": "bridge loans"},
             "conditions": [{"condition_id": "credit-condition", "text": "Conditions precedent satisfied"}],
             "exceptions": [], "timing": None,
             "business_scope": {"scenario_role": "lender_funding_condition"},
             "trigger": {"event": "borrowing request"},
             "evidence": [{"source_id": "source-funding"}]},
            {"statement_id": "transaction-condition", "actor": {"name": "Parent", "role": "parent"},
             "action": {"modality": "prohibited", "verb": "condition", "object": "transaction completion"},
             "conditions": [], "exceptions": [], "timing": None,
             "business_scope": {"scenario_role": "transaction_completion_condition"},
             "trigger": None, "evidence": [{"source_id": "source-merger"}]},
        ],
    }


class TermScenarioMappingTests(unittest.TestCase):
    def setUp(self):
        config = json.loads((ROOT / "config/assumptions.json").read_text())
        self.assumptions = copy.deepcopy(config["bio_techne"])
        self.assumptions["version"] = config["version"]

    def test_supported_dates_create_dated_scenarios_but_not_factual_elections(self):
        condition = {"condition_id": "regulatory-open",
                     "text": "Regulatory condition remains unsatisfied"}
        mapped = map_structured_terms_to_scenario_inputs([
            extension_term("first", "2027-06-25", "automatic", conditions=[condition]),
            extension_term("final", "2027-09-25", "permitted", conditions=[condition]),
            financing_term(),
        ], self.assumptions)
        rows = {row["scenario_id"]: row for row in mapped["scenario_inputs"]}
        # Calendar arithmetic derived independently: Mar 15 -> Jun 25 is 102
        # days; Mar 15 -> Sep 25 is 194 days.
        self.assertEqual(rows["first_extension"]["delay_days"], 102)
        self.assertEqual(rows["final_extension"]["delay_days"], 194)
        self.assertEqual(mapped["contractual_facts"]["extension_dates"][0]["designation"], "fact")
        self.assertEqual(len(mapped["hypothetical_elections"]), 1)
        election = mapped["hypothetical_elections"][0]
        self.assertEqual(election["fact_id"], "final")
        self.assertEqual(election["designation"], "assumption")
        condition_assumptions = [x for x in mapped["scenario_assumptions"]
                                 if x["name"] == "extension_conditions_satisfied"]
        self.assertEqual({x["fact_id"] for x in condition_assumptions}, {"first", "final"})

    def test_funding_roles_remain_distinct_and_do_not_assert_availability(self):
        mapped = map_structured_terms_to_scenario_inputs([
            extension_term("only", "2027-06-25", "automatic"), financing_term()
        ], self.assumptions)
        facts = mapped["contractual_facts"]["funding_conditions"]
        self.assertEqual({x["scenario_role"] for x in facts},
                         {"lender_funding_condition", "transaction_completion_condition"})
        completion = [x for x in mapped["scenario_assumptions"]
                      if x["name"] == "transaction_completed"]
        self.assertEqual(len(completion), 2)
        self.assertTrue(all(set(x["related_funding_fact_ids"]) ==
                            {"lender-condition", "transaction-condition"}
                            for x in completion))
        self.assertNotIn("financing_available", mapped)

    def test_candidate_missing_and_materially_unresolved_dates_block(self):
        candidate = extension_term("candidate", "2027-06-25", "automatic",
                                   status="candidate")
        missing = extension_term("missing", None, "automatic")
        unresolved = extension_term("unresolved", "2027-09-25", "automatic")
        unresolved["unresolved"] = [{"reason": "missing_schedule",
                                      "expression": "Schedule 1",
                                      "materiality": "material"}]
        mapped = map_structured_terms_to_scenario_inputs(
            [candidate, missing, unresolved], self.assumptions)
        self.assertEqual(mapped["scenario_inputs"], [])
        self.assertEqual({x["scenario"] for x in mapped["blocked_scenarios"]},
                         {"first_extension", "final_extension"})
        self.assertTrue(all(not x["usable_for_scenarios"]
                            for x in mapped["contractual_facts"]["extension_dates"]))
        self.assertTrue(all(x["designation"] == "candidate"
                            for x in mapped["contractual_facts"]["extension_dates"]))

    def test_statement_level_material_unresolved_date_blocks(self):
        term = extension_term("statement-open", "2027-06-25", "automatic")
        term["statements"][0]["unresolved"] = [{
            "reason": "missing_exception", "expression": "referenced proviso",
            "materiality": "material"}]
        mapped = map_structured_terms_to_scenario_inputs([term], self.assumptions)
        self.assertEqual(mapped["scenario_inputs"], [])
        self.assertTrue(all(not fact["usable_for_scenarios"]
                            for fact in mapped["contractual_facts"]["extension_dates"]))

    def test_single_supported_date_is_labeled_for_both_required_delay_cases(self):
        mapped = map_structured_terms_to_scenario_inputs(
            [extension_term("only", "2027-06-25", "automatic")],
            self.assumptions)
        rows = mapped["scenario_inputs"]
        self.assertEqual([x["scenario_id"] for x in rows],
                         ["first_extension", "final_extension"])
        self.assertTrue(all("Single supported extension date" in x["note"] for x in rows))

    def test_neutral_failure_is_requirement_case_and_directional_stresses_remain(self):
        config = json.loads((ROOT / "config/assumptions.json").read_text())
        result = run_analytics({"role": "development", "transaction_type": "merger"},
                               [], [], config)
        rows = {(row["scenario_id"], row["strategy"]): row for row in result["rows"]}
        self.assertIn(("failure", "unhedged"), rows)
        self.assertIn(("failure_rates_down_25", "unhedged"), rows)
        self.assertIn(("failure_rates_up_25", "unhedged"), rows)
        # Independently: no issuance and 0bp move produces no unhedged cost;
        # contingent hedge retains only the assumed 20bp of USD 4bn fee.
        self.assertEqual(rows[("failure", "unhedged")]["net_incremental_cost_pv"], 0)
        self.assertEqual(rows[("failure", "deal_contingent_payer_swap")]
                         ["net_incremental_cost_pv"], 8_000_000)


if __name__ == "__main__":
    unittest.main()
