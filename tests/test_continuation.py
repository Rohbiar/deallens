import copy
import io
import json
import unittest
from pathlib import Path

from deallens.analytics import scenario
from deallens.provider import OpenAIProvider, ProviderError
from deallens.semantic import select_chunks, validate_proposals
from test_semantic_review import fixture


class ContinuationControls(unittest.TestCase):
    def test_iso_currency_consideration_retrieved(self):
        doc, _, _ = fixture()
        doc['chunks'][0]['text'] = 'The consideration per Target Share shall be in cash only and shall be at least EUR 41.50 per Target Share (the Offer Price).'
        self.assertTrue(select_chunks(doc, 'consideration_per_share', 'transaction-agreement'))

    def test_retrieval_includes_preceding_page_context(self):
        doc, _, _ = fixture()
        hit = doc['chunks'][0]
        hit.update(page=2, chunk_id='hit')
        previous = {**hit, 'page':1, 'chunk_id':'previous', 'text':'Exception applies only to awards granted before the cutoff.'}
        doc['chunks'] = [previous, hit]
        self.assertIn('previous', [c['chunk_id'] for c in select_chunks(doc, 'rsus', 'transaction-agreement')])

    def test_nonfinite_nested_model_value_rejected(self):
        doc, req, proposal = fixture()
        proposal['normalized_value_json'] = '{"amount":1e999}'
        with self.assertRaises(ValueError):
            validate_proposals({'proposals':[proposal]}, req, doc, 'test', .9)

    def test_malformed_citation_rejected(self):
        doc, req, proposal = fixture()
        proposal['citations'] = [None]
        with self.assertRaises(ValueError):
            validate_proposals({'proposals':[proposal]}, req, doc, 'test', .9)

    def test_malformed_provider_envelopes_fail_safely(self):
        for body in [[], {'status':'completed', 'output':[None]}, {'status':'completed','output':None}]:
            with self.subTest(body=body):
                provider = OpenAIProvider('synthetic', opener=lambda *a, **k: io.BytesIO(json.dumps(body).encode()))
                with self.assertRaises(ProviderError):
                    provider({'model':'synthetic','system':'test','chunks':[]})

    def test_nonfinite_financial_inputs_rejected(self):
        base = json.loads((Path(__file__).resolve().parents[1]/'config/assumptions.json').read_text())['bio_techne']
        base['version'] = 'test'
        for key in ['notional', 'base_probability', 'option_premium_bp_notional']:
            a = copy.deepcopy(base)
            a[key] = float('nan')
            with self.subTest(key=key), self.assertRaises(ValueError):
                scenario(a, 'payer_option')
        with self.assertRaises(ValueError):
            scenario(base, 'unhedged', benchmark_bp=float('inf'))
