import unittest

from deallens.extract import validate_evidence
from deallens.ingest import normalize
from deallens.provisions import provision_records
from deallens.semantic import extract_semantic, select_request_context


def document():
    raw = (
        "Section 8.01 Termination.\n"
        "Parent may extend the Outside Date by written notice subject to Section 8.02.\n"
        "Section 8.02 Extension Conditions.\n"
        "The regulatory condition must remain unsatisfied and Parent must not be in breach.\n"
        "Section 8.03 End.\nEnd."
    )
    text = normalize(raw)
    page = {"page": 1, "raw_text": raw, "text": text, "machine_readable": True,
            "document_layer": "transaction-agreement", "locator": "demo:abc:p1"}
    chunk = {"page": 1, "document_layer": "transaction-agreement", "text": text,
             "start": 0, "end": len(text), "chunk_id": "legacy-chunk"}
    return {"document_id": "demo", "sha256": "abc", "pages": [page], "chunks": [chunk]}


class SemanticContextTests(unittest.TestCase):
    def test_priority_field_uses_displayed_context_sources(self):
        doc = document(); records = provision_records(doc, "run")
        source_record = next(r for r in records
                             if r["field_name"] == "extension_dates_and_conditions")
        chunks, metadata = select_request_context(
            doc, "extension_dates_and_conditions", "transaction-agreement",
            context_records=records)
        bundle_ids = {s["source_id"] for s in source_record["context_bundle"]["sources"]}
        self.assertEqual({c["chunk_id"] for c in chunks}, bundle_ids)
        self.assertEqual(metadata["selected_source_ids"], [c["chunk_id"] for c in chunks])
        self.assertFalse(metadata["downstream_truncated"])
        self.assertEqual(metadata["completeness"], "not_established")
        self.assertTrue(all(validate_evidence(c, doc) for c in chunks))

    def test_downstream_budget_discloses_every_omitted_source(self):
        doc = document(); records = provision_records(doc, "run")
        chunks, metadata = select_request_context(
            doc, "extension_dates_and_conditions", "transaction-agreement",
            max_chars=120, context_records=records)
        bundle = next(r["context_bundle"] for r in records
                      if r["field_name"] == "extension_dates_and_conditions")
        all_ids = {s["source_id"] for s in bundle["sources"]}
        self.assertEqual(all_ids, set(metadata["selected_source_ids"]) |
                         set(metadata["omitted_source_ids"]))
        self.assertTrue(metadata["downstream_truncated"])
        self.assertLessEqual(sum(len(c["text"]) for c in chunks), 120)

    def test_request_and_audit_bind_to_same_context(self):
        doc = document(); seen = []
        def provider(request):
            seen.append(request)
            chunk = request["chunks"][0]
            return {"proposals": [{
                "field_name": "extension_dates_and_conditions",
                "citations": [{"chunk_id": chunk["chunk_id"],
                               "evidence": chunk["text"]}],
                "normalized_value_json": "null", "raw_value": None,
                "currency": None, "value_qualifier": None,
                "confidence": .5, "limitations": "Synthetic adapter test."
            }]}
        records, audit = extract_semantic(
            doc, "run", provider, "test-model",
            fields=["extension_dates_and_conditions"], max_calls=1)
        request = seen[0]
        self.assertEqual(request["retrieval_context"]["selected_source_ids"],
                         [c["chunk_id"] for c in request["chunks"]])
        context_audit = next(a for a in audit if "retrieval_context_status" in a)
        self.assertEqual(context_audit["retrieval_context_status"]["completeness"],
                         "not_established")
        self.assertIn("retrieval_context_sha256", context_audit)
        self.assertEqual(records[0]["status"], "low_confidence")

    def test_scalar_field_retains_chunk_retrieval(self):
        doc = document()
        chunks, metadata = select_request_context(
            doc, "outside_or_long_stop_date", "transaction-agreement")
        self.assertIsNone(metadata)
        self.assertEqual([c["chunk_id"] for c in chunks], ["legacy-chunk"])


if __name__ == "__main__":
    unittest.main()
