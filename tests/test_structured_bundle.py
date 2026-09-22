import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from deallens.cli import build_structured_terms
from deallens.storage import save


def context(field="extension_dates_and_conditions", evidence=None):
    evidence = evidence or (
        "if all of the conditions to Closing are satisfied, the Outside Date "
        "shall automatically extend to June 25, 2027"
    )
    section_id = "transaction-agreement:8.01:1"
    source = {"source_id": "source:abc:1:0-120", "section_id": section_id,
              "document_id": "demo", "document_sha256": "abc",
              "document_layer": "transaction-agreement", "page": 1,
              "start": 0, "end": len(evidence), "evidence": evidence,
              "section": "Section 8.01", "locator": "demo:abc:p1:chars0-120"}
    return {"schema_version": "retrieval-context/v1", "source_hash": "abc",
            "document_id": "demo", "root_section_ids": [section_id],
            "section_ids": [section_id],
            "sections": [{"section_id": section_id,
                          "document_layer": "transaction-agreement",
                          "number": "8.01", "title": "Termination", "root": True,
                          "source_ids": [source["source_id"]], "boundary": "next_section"}],
            "definitions": [], "sources": [source], "edges": [], "unresolved": [],
            "budget": {"truncated": False}, "completeness": "not_established"}


def source_record(field="extension_dates_and_conditions", evidence=None):
    return {"field_name": field, "status": "source_excerpt",
            "context_bundle": context(field, evidence)}


class StructuredBundleTests(unittest.TestCase):
    def test_builds_source_bound_candidate_without_promotion(self):
        terms = build_structured_terms([source_record()])
        self.assertEqual(len(terms), 1)
        self.assertEqual(terms[0]["status"], "candidate")
        self.assertEqual(terms[0]["review_status"], "unreviewed")
        self.assertTrue(terms[0]["statements"])
        self.assertEqual(terms[0]["document_sha256"], "abc")

    def test_no_match_is_retained_as_valid_unresolved_term(self):
        terms = build_structured_terms([
            source_record("remedy_limitations", "The parties will cooperate generally.")])
        self.assertEqual(len(terms), 1)
        self.assertEqual(terms[0]["status"], "unresolved")
        self.assertEqual(terms[0]["statements"], [])
        self.assertEqual(terms[0]["unresolved"][-1]["reason"],
                         "no_recognized_atomic_statement")

    def test_sqlite_persists_terms_append_only_by_run(self):
        term = build_structured_terms([source_record()])[0]
        document = {"document_id": "demo", "sha256": "abc", "url": "https://example.invalid",
                    "page_count": 0, "pages": []}
        bundle = {"document": document, "extractions": [], "comparisons": [],
                  "analytics": {"rows": []}, "structured_terms": [term]}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "audit.sqlite"
            for run_id in ("run-one", "run-two"):
                manifest = {"run_id": run_id, "started_at": "2026-09-21T00:00:00Z",
                            "code_version": "test", "assumptions_version": "test"}
                save(path, manifest, [bundle])
            with sqlite3.connect(path) as db:
                rows = db.execute(
                    "SELECT run_id,status,record_json FROM structured_terms ORDER BY run_id"
                ).fetchall()
            self.assertEqual([row[0] for row in rows], ["run-one", "run-two"])
            self.assertTrue(all(row[1] == "candidate" for row in rows))
            self.assertTrue(all(json.loads(row[2])["term_id"] == term["term_id"]
                                for row in rows))


if __name__ == "__main__":
    unittest.main()
