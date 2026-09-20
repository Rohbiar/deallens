import copy
import io
import json
import unittest
from deallens.citations import passage_catalog, resolve_citations
from deallens.provider import OpenAIProvider
from deallens.semantic import validate_proposals
from test_semantic_review import fixture

class CitationProtocolTests(unittest.TestCase):
    def test_catalog_preserves_exact_unicode_text_and_offsets(self):
        text=('Curly “quotes”, Unicode € amounts and source wording. '*40)
        chunk={'chunk_id':'source','page':2,'text':text+'Unique closing condition.'}
        for p in passage_catalog([chunk]):
            self.assertEqual(p['text'],text.__add__('Unique closing condition.')[p['start']:p['end']])
            self.assertEqual(chunk['text'].count(p['text']),1)

    def test_unknown_ids_and_model_supplied_quotes_rejected(self):
        doc,_,proposal=fixture();catalog=passage_catalog(doc['chunks'])
        for citation in [{'citation_id':'unknown'},{'citation_id':'p0','evidence':'fabricated'},{'citation_id':None}]:
            p=copy.deepcopy(proposal);p['citations']=[citation]
            with self.assertRaises(ValueError):resolve_citations({'proposals':[p]},catalog)

    def test_transport_enum_reconstructs_citation_but_not_verified_fact(self):
        doc,req,proposal=fixture();seen=[]
        def opener(request,timeout):
            body=json.loads(request.data);seen.append(body)
            payload=json.loads(body['input']);ident=payload['passages'][0]['citation_id']
            p=copy.deepcopy(proposal);p['citations']=[{'citation_id':ident}]
            return io.BytesIO(json.dumps({'id':'synthetic','status':'completed','output':[{'content':[{'type':'output_text','text':json.dumps({'proposals':[p]})}]}]}).encode())
        provider=OpenAIProvider('synthetic-placeholder',opener=opener)
        req['system']='Synthetic test';out=provider(req)
        schema=seen[0]['text']['format']['schema']
        self.assertEqual(schema['properties']['proposals']['items']['properties']['citations']['items']['properties']['citation_id']['enum'],['p0'])
        record=validate_proposals(out,req,doc,'r',.9)[0]
        self.assertEqual(record['evidence'],doc['pages'][0]['text'])
        self.assertIsNone(record['normalized_value'])
        self.assertNotEqual(record['review_status'],'verified')
        self.assertIn('passage_catalog_sha256',provider.last_metadata)
