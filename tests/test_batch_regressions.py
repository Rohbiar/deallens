"""Controls prompted by the broader live batch; not semantic accuracy tests."""
import copy
import unittest
from test_semantic_review import fixture
from deallens.semantic import extract_semantic, select_chunks

class BatchRegressions(unittest.TestCase):
    def test_rejection_reasons_are_distinct_and_do_not_echo_output(self):
        for mutation, expected in [
            (lambda p: p['citations'][0].update(chunk_id='untrusted-secret'), 'Citation references an unretrieved chunk'),
            (lambda p: p['citations'][0].update(evidence='untrusted-secret fabricated quotation'), 'Citation excerpt is not exact in its named chunk'),
            (lambda p: p['citations'][0].update(evidence='short'), 'Citation excerpt is missing or too short'),
        ]:
            with self.subTest(expected=expected):
                doc, _, proposal = fixture(); mutation(proposal)
                records, audit = extract_semantic(doc, 'test', lambda _: {'proposals':[proposal]}, 'test', fields=['rsus'])
                self.assertEqual(records, [])
                failure = next(a for a in audit if a['status']=='invalid_output')
                self.assertEqual(failure['validation_reason'], expected)
                self.assertNotIn('untrusted-secret', str(failure))

    def test_operative_borrowing_clause_precedes_repeated_definition_hits(self):
        doc, _, _ = fixture()
        base = doc['chunks'][0]
        doc['chunks'] = []
        for n in range(20):
            text = ('conditions to funding ' * 20) if n < 19 else 'Conditions to Initial Borrowing on Closing Date. Receipt of the borrowing request is required.'
            doc['chunks'].append({**base, 'page':n+1, 'chunk_id':str(n), 'text':text})
        result = select_chunks(doc, 'financing_conditions', 'transaction-agreement', max_chars=1800)
        self.assertEqual(result[0]['chunk_id'], '19')
        self.assertLessEqual(sum(len(c['text']) for c in result), 1800)
