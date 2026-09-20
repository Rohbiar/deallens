import copy
import io
import json
import unittest
import ssl
from urllib.error import URLError
from unittest.mock import patch
from pathlib import Path

from deallens.analytics import scenario
from deallens.provider import OpenAIProvider, ProviderError
from deallens.semantic import select_chunks, validate_proposals, extract_semantic
from test_semantic_review import fixture


class ContinuationControls(unittest.TestCase):
    def test_financing_proposals_require_boolean(self):
        doc, req, proposal = fixture()
        req['fields'] = ['financing_condition']
        proposal['field_name'] = 'financing_condition'
        with self.assertRaisesRegex(ValueError, 'JSON boolean'):
            validate_proposals({'proposals':[proposal]}, req, doc, 'test', .9)
        proposal['normalized_value_json'] = 'false'
        record = validate_proposals({'proposals':[proposal]}, req, doc, 'test', .9)[0]
        self.assertIs(record['candidate_value'], False)
        self.assertIsNone(record['normalized_value'])

    def test_invalid_json_audit_explains_rejection(self):
        doc, _, proposal = fixture()
        proposal['normalized_value_json'] = 'False'
        _, audit = extract_semantic(doc, 'test', lambda _: {'proposals':[proposal]}, 'synthetic', fields=['rsus'])
        failure = next(a for a in audit if a['status']=='invalid_output')
        self.assertEqual(failure['validation_reason'], 'Invalid JSON inside normalized_value_json')

    def test_provider_failure_is_not_budget_exhaustion(self):
        doc, _, _ = fixture()
        def fail(_): raise ProviderError('Synthetic connection failure')
        _, audit = extract_semantic(doc, 'test', fail, 'synthetic', fields=['rsus','rsus'], max_calls=4)
        self.assertTrue(any(a['status']=='skipped_after_provider_error' for a in audit))
        self.assertFalse(any(a['status']=='budget_exhausted' for a in audit))

    def test_provider_preserves_tls_verification(self):
        with patch('deallens.provider.urllib.request.build_opener') as build:
            OpenAIProvider('synthetic')
        handler = build.call_args.args[1]
        self.assertEqual(handler._context.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(handler._context.check_hostname)
        self.assertGreater(handler._context.cert_store_stats()['x509_ca'], 0)

    def test_certificate_failure_has_specific_safe_diagnostic(self):
        def opener(*args, **kwargs):
            raise URLError(ssl.SSLCertVerificationError(1, 'private network detail'))
        provider = OpenAIProvider('synthetic', opener=opener)
        with self.assertRaisesRegex(ProviderError, 'TLS certificate verification failed') as caught:
            provider({'model':'synthetic','system':'test','chunks':[]})
        self.assertNotIn('private network detail', str(caught.exception))

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
