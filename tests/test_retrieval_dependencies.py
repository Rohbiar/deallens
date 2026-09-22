import json
import unittest
from pathlib import Path

from deallens.extract import validate_evidence
from deallens.ingest import ingest
from deallens.provisions import provision_records, section_index
from deallens.retrieval_context import build_context_bundle
from tests.test_provisions import document


class RetrievalDependencyTests(unittest.TestCase):
    def bundle(self, pages, *, layers=None, root=0, **limits):
        doc = document(pages, layers)
        sections = section_index(doc)
        return doc, sections, build_context_bundle(doc, sections, [sections[root]], **limits)

    def test_recursive_cycle_is_reported_and_bounded(self):
        doc, sections, bundle = self.bundle([
            "Section 1.01 First.\nSee Section 1.02.\n"
            "Section 1.02 Second.\nSee Section 1.03.\n"
            "Section 1.03 Third.\nSee Section 1.01.\n"
            "Section 1.04 End.\nEnd."
        ])
        self.assertEqual(bundle["section_ids"], [
            "transaction-agreement:1.01:1",
            "transaction-agreement:1.02:1",
            "transaction-agreement:1.03:1",
        ])
        self.assertTrue(any(x["reason"] == "cycle_detected" for x in bundle["unresolved"]))
        self.assertTrue(all(validate_evidence(source, doc) for source in bundle["sources"]))

    def test_duplicate_numbers_do_not_cross_instrument_boundaries(self):
        doc, sections, bundle = self.bundle(
            [
                "Section 2.01 Agreement Terms.\nSee Section 5.01.\nSection 2.02 End.\nEnd.",
                "5.01 Loan Terms.\nWrong instrument.\n5.02 End.\nEnd.",
            ],
            layers=["transaction-agreement", "financing-agreement"],
        )
        edge = next(e for e in bundle["edges"] if e["target"].get("section_number") == "5.01")
        self.assertEqual(edge["reason"], "instrument_boundary")
        self.assertIsNone(edge["to_section_id"])

    def test_same_instrument_duplicate_heading_is_ambiguous(self):
        _, _, bundle = self.bundle([
            "Section 1.01 Root.\nSee Section 5.01.\n"
            "Section 5.01 First Copy.\nOne.\n"
            "Section 5.01 Second Copy.\nTwo.\n"
            "Section 6.01 End.\nEnd."
        ])
        edge = next(e for e in bundle["edges"] if e["target"].get("section_number") == "5.01")
        self.assertEqual(edge["status"], "ambiguous")
        self.assertEqual(edge["reason"], "ambiguous_target")

    def test_multi_reference_expression_preserves_subsections(self):
        _, _, bundle = self.bundle([
            "Section 1.01 Root.\nSubject to Sections 5.01(a), (b), and 5.02.\n"
            "Section 5.01 Conditions.\nFirst.\n"
            "Section 5.02 Exceptions.\nSecond.\n"
            "Section 6.01 End.\nEnd."
        ])
        edges = [e for e in bundle["edges"] if e["from_section_id"].endswith("1.01:1")]
        self.assertEqual([e["target"]["section_number"] for e in edges], ["5.01", "5.02"])
        self.assertEqual(edges[0]["target"]["subsections"], ["a", "b"])
        self.assertTrue(all(e["status"] == "resolved" for e in edges))

    def test_missing_schedule_remains_an_explicit_dependency(self):
        _, _, bundle = self.bundle([
            "Section 1.01 Root.\nThe obligations are set out in Schedule 4.2.\n"
            "Section 1.02 End.\nEnd."
        ])
        unresolved = next(x for x in bundle["unresolved"] if x["target"].get("schedule"))
        self.assertEqual(unresolved["reason"], "missing_target")
        self.assertEqual(bundle["completeness"], "not_established")

    def test_budget_exhaustion_does_not_attach_partial_dependency(self):
        _, sections, bundle = self.bundle([
            "Section 1.01 Root.\nSee Section 2.01.\n"
            "Section 2.01 Long Terms.\n" + "condition " * 100 + "\n"
            "Section 3.01 End.\nEnd."
        ], max_chars=80)
        edge = next(e for e in bundle["edges"] if e["target"].get("section_number") == "2.01")
        self.assertEqual(edge["status"], "budget_exhausted")
        self.assertTrue(bundle["budget"]["truncated"])
        self.assertIn("character_budget", bundle["budget"]["exhausted_by"])
        self.assertNotIn(sections[1]["section_id"], bundle["section_ids"])

    def test_stable_attribution_and_definition_evidence(self):
        doc, sections, bundle = self.bundle([
            "Section 1.01 Defined Terms.\n"
            "\u201cApplicable Rate\u201d means the rate in the grid.\n"
            "\u201cOther Term\u201d means something else.\n"
            "Section 2.01 Interest.\nInterest uses the Applicable Rate.\n"
            "Section 3.01 End.\nEnd."
        ], root=1, definition_terms=["Applicable Rate"])
        definition = bundle["definitions"][0]
        source_map = {s["source_id"]: s for s in bundle["sources"]}
        self.assertTrue(definition["source_ids"])
        self.assertTrue(all(source_map[i]["definition_id"] == definition["definition_id"]
                            for i in definition["source_ids"]))
        self.assertTrue(all(s["source_id"] and s["section_id"] for s in bundle["sources"]))
        self.assertEqual(bundle["source_hash"], doc["sha256"])
        json.dumps(bundle)

    def test_unrecognized_reference_is_not_silently_complete(self):
        _, _, bundle = self.bundle([
            "Section 1.01 Root.\nSee Sections Five and Six for details.\n"
            "Section 1.02 End.\nEnd."
        ])
        self.assertTrue(bundle["recognition"]["unrecognized_expressions"])
        self.assertTrue(any(x["reason"] == "unrecognized_reference" for x in bundle["unresolved"]))

    def test_partially_parsed_range_is_reported(self):
        _, _, bundle = self.bundle([
            "Section 1.01 Root.\nSee Sections 5.01 through 5.03.\n"
            "Section 5.01 First.\nOne.\nSection 5.03 Third.\nThree.\n"
            "Section 6.01 End.\nEnd."
        ])
        self.assertTrue(any("through" in x for x in bundle["recognition"]["unrecognized_expressions"]))

    def test_extension_and_fee_continuations_in_all_supplied_sources(self):
        root = Path(__file__).resolve().parents[1]
        source_config = json.loads((root / "config/sources.json").read_text())
        expected = {
            "bio_techne": {
                "extension_dates_and_conditions": {71, 72, 73},
                "fee_triggers_and_tails": {71, 72, 73, 74, 75, 76},
            },
            "organon": {
                "extension_dates_and_conditions": {86, 87},
                "fee_triggers_and_tails": {87, 88, 89, 90},
            },
            "uber_delivery_hero": {
                "extension_dates_and_conditions": {12, 13, 14},
                "fee_triggers_and_tails": {34, 35},
            },
        }
        for source in source_config:
            doc = ingest(root / "data/sources" / f"{source['document_id']}.pdf", source)
            records = provision_records(doc, "source-test")
            for field, pages in expected[source["document_id"]].items():
                record = next(r for r in records if r["field_name"] == field)
                self.assertTrue(pages.issubset({s["page"] for s in record["evidence_sources"]}))
                self.assertTrue(all(validate_evidence(s, doc) for s in record["context_bundle"]["sources"]))
                self.assertEqual(record["context_bundle"]["source_hash"], doc["sha256"])


if __name__ == "__main__":
    unittest.main()
