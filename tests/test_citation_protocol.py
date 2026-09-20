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
            p=copy.deepcopy(proposal);p.pop('normalized_value_json');p['normalized_value']={'summary':'Synthetic','details':[]};p['citations']=[citation]
            with self.assertRaises(ValueError):resolve_citations({'proposals':[p]},catalog)

    def test_transport_enum_reconstructs_citation_but_not_verified_fact(self):
        doc,req,proposal=fixture();seen=[]
        def opener(request,timeout):
            body=json.loads(request.data);seen.append(body)
            payload=json.loads(body['input']);ident=payload['passages'][0]['citation_id']
            p=copy.deepcopy(proposal);p.pop('normalized_value_json');p['normalized_value']={'summary':'RSUs retain service vesting','details':[]};p['citations']=[{'citation_id':ident}]
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

    def test_typed_values_handle_quotes_without_a_second_model_json_parse(self):
        from deallens.citations import typed_value
        for value in [False,73.0,None,'2027-03-25',{'summary':'A “Burdensome Condition” is defined.','details':[{'label':'scope','value':'The text contains "quotes" and a \n newline.'}]}]:
            self.assertEqual(json.loads(typed_value(value)),value)
        for value in [float('nan'),{'unknown':'shape'},{'summary':'x','details':[{'label':'x','value':{'nested':'object'}}]}]:
            with self.assertRaises(ValueError):typed_value(value)
