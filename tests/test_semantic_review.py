import copy
import io
import json
import tempfile
import shutil
import unittest
from pathlib import Path
from urllib.error import HTTPError
from deallens.provider import OpenAIProvider,ProviderError
from deallens.semantic import extract_semantic,validate_proposals,identify,select_chunks
from deallens.extract import evidence_record,comparison
from deallens.review import apply_decisions,packet
from deallens.qa import answer,UNSUPPORTED

def fixture():
    text='Each outstanding RSU becomes a cash-based award and remains subject to service-based vesting.'
    page={'page':1,'text':text,'document_layer':'transaction-agreement','locator':'demo:abc:p1','machine_readable':True}
    chunk={'page':1,'document_layer':'transaction-agreement','text':text,'start':0,'end':len(text),'chunk_id':'demo:abc:p1:c0'}
    doc={'document_id':'demo','sha256':'abc','pages':[page],'chunks':[chunk]}
    request={'model':'test-model','fields':['rsus'],'chunks':[chunk]}
    proposal={'field_name':'rsus','citations':[{'chunk_id':chunk['chunk_id'],'evidence':text}],
              'normalized_value_json':json.dumps({'summary':'RSUs become cash awards with continued service vesting.'}),
              'raw_value':None,'currency':None,'value_qualifier':None,'confidence':.96,'limitations':'Only supplied clause examined.'}
    return doc,request,proposal

class SemanticTests(unittest.TestCase):
    def test_valid_model_proposal_cannot_approve_itself(self):
        doc,req,p=fixture();p['review_status']='verified'
        r=validate_proposals({'proposals':[p]},req,doc,'r',.9)[0]
        self.assertIsNone(r['normalized_value']);self.assertEqual(r['review_status'],'exception')
        self.assertEqual(r['candidate_value']['summary'],'RSUs become cash awards with continued service vesting.')
    def test_fabricated_evidence_rejected(self):
        doc,req,p=fixture();p['citations'][0]['evidence']='All RSUs vest immediately and are paid in full.'
        with self.assertRaises(ValueError):validate_proposals({'proposals':[p]},req,doc,'r',.9)
    def test_unretrieved_chunk_rejected(self):
        doc,req,p=fixture();p['citations'][0]['chunk_id']='different-document'
        with self.assertRaises(ValueError):validate_proposals({'proposals':[p]},req,doc,'r',.9)
    def test_low_confidence_remains_null(self):
        doc,req,p=fixture();p['confidence']=.3
        r=validate_proposals({'proposals':[p]},req,doc,'r',.9)[0]
        self.assertEqual(r['status'],'low_confidence');self.assertIsNone(r['normalized_value'])
    def test_nonfinite_json_rejected(self):
        doc,req,p=fixture();p['normalized_value_json']='{"value": NaN}'
        with self.assertRaises(ValueError):validate_proposals({'proposals':[p]},req,doc,'r',.9)
    def test_call_budget_and_audit(self):
        doc,req,p=fixture();calls=[]
        def provider(r):calls.append(r);return {'proposals':[p]}
        records,audit=extract_semantic(doc,'r',provider,'test',fields=['rsus','award_cohort_differences'],max_calls=1)
        self.assertEqual(len(calls),1);self.assertEqual(len(records),1)
        self.assertTrue(any(a['status']=='proposals_retained' for a in audit))
        self.assertIn('request_sha256',next(a for a in audit if a['status']=='proposals_retained'))
    def test_retrieval_budget(self):
        doc,_,_=fixture();doc['chunks']*=50
        self.assertLessEqual(sum(len(c['text']) for c in select_chunks(doc,'rsus','transaction-agreement',max_chars=1800)),1800)

class ProviderTests(unittest.TestCase):
    def response(self,output,status='completed'):
        return io.BytesIO(json.dumps({'id':'test-id','status':status,'model':'test','usage':{'input_tokens':8,'output_tokens':5},
                                     'output':[{'content':output}]}).encode())
    def request(self):return {'model':'test','system':'instructions','fields':['rsus'],'chunks':[],'tools':[]}
    def test_transport_schema_and_no_storage(self):
        seen=[]
        def opener(req,timeout):seen.append(json.loads(req.data));return self.response([{'type':'output_text','text':'{"proposals":[]}'}])
        provider=OpenAIProvider('test-placeholder',opener=opener)
        self.assertEqual(provider(self.request()),{'proposals':[]})
        self.assertFalse(seen[0]['store']);self.assertTrue(seen[0]['text']['format']['strict'])
        self.assertNotIn('test-placeholder',json.dumps(provider.last_metadata))
    def test_incomplete_output_not_accepted(self):
        provider=OpenAIProvider('test-placeholder',opener=lambda *a,**k:self.response([],status='incomplete'))
        with self.assertRaises(ProviderError):provider(self.request())
    def test_refusal_not_accepted(self):
        provider=OpenAIProvider('test-placeholder',opener=lambda *a,**k:self.response([{'type':'refusal','refusal':'no'}]))
        with self.assertRaises(ProviderError):provider(self.request())
    def test_auth_failure_does_not_leak_body_or_retry(self):
        calls=[]
        def opener(*a,**k):calls.append(1);raise HTTPError('https://api.openai.com',401,'secret-detail',{},None)
        provider=OpenAIProvider('test-placeholder',opener=opener)
        with self.assertRaises(ProviderError) as cm:provider(self.request())
        self.assertEqual(len(calls),1);self.assertNotIn('secret-detail',str(cm.exception))
    def test_rate_limit_has_bounded_retry(self):
        calls=[]
        def opener(*a,**k):
            calls.append(1)
            if len(calls)<3:raise HTTPError('https://api.openai.com',429,'limit',{},None)
            return self.response([{'type':'output_text','text':'{"proposals":[]}'}])
        provider=OpenAIProvider('test-placeholder',opener=opener,sleeper=lambda _:None)
        provider(self.request());self.assertEqual(provider.last_metadata['attempts'],3)

class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.doc,req,p=fixture()
        self.records=validate_proposals({'proposals':[p]},req,self.doc,'base',.9)
        self.bundles=[{'document':self.doc,'extractions':self.records}]
        self.manifest={'run_id':'base'}
        self.submission={'base_run_id':'base','reviewer':'TEST REVIEWER - SYNTHETIC FIXTURE ONLY','human_review_attested':True,
                         'decisions':[{'document_id':'demo','field_name':'rsus','document_layer':'transaction-agreement','action':'approve',
                                       'record_ids':[self.records[0]['record_id']],'reason':'Test fixture reviewed against the complete supplied sentence.',
                                       'complete_field_layer':True}]}
    def test_approval_preserves_original_and_enables_strict_answer(self):
        original=copy.deepcopy(self.bundles)
        new,events=apply_decisions(self.manifest,self.bundles,self.submission,'reviewed')
        self.assertEqual(self.bundles,original)
        rs=new[0]['extractions'];self.assertEqual(rs[0]['status'],'superseded')
        self.assertEqual(rs[-1]['review_status'],'verified');self.assertEqual(events[0]['base_run_id'],'base')
        self.assertNotEqual(answer('awards',rs,comparison(rs),strict=True)['answer'],UNSUPPORTED)
    def test_missing_attestation_rejected(self):
        self.submission['human_review_attested']=False
        with self.assertRaises(ValueError):apply_decisions(self.manifest,self.bundles,self.submission,'r')
    def test_stale_review_rejected(self):
        self.submission['base_run_id']='old'
        with self.assertRaises(ValueError):apply_decisions(self.manifest,self.bundles,self.submission,'r')
    def test_unknown_record_rejected(self):
        self.submission['decisions'][0]['record_ids']=['fake']
        with self.assertRaises(ValueError):apply_decisions(self.manifest,self.bundles,self.submission,'r')
    def test_missing_scope_attestation_rejected(self):
        self.submission['decisions'][0]['complete_field_layer']=False
        with self.assertRaises(ValueError):apply_decisions(self.manifest,self.bundles,self.submission,'r')
    def test_reject_keeps_history_but_cannot_answer(self):
        self.submission['decisions'][0]['action']='reject'
        b,_=apply_decisions(self.manifest,self.bundles,self.submission,'r');rs=b[0]['extractions']
        self.assertEqual(rs[0]['status'],'rejected');self.assertIsNotNone(rs[0]['candidate_value'])
        self.assertEqual(answer('awards',rs,comparison(rs))['answer'],UNSUPPORTED)
    def test_tampered_source_rejected(self):
        self.doc['pages'][0]['text']='different content'
        with self.assertRaises(ValueError):apply_decisions(self.manifest,self.bundles,self.submission,'r')
    def test_export_has_no_preapproved_decisions(self):
        p=packet(self.manifest,self.bundles)
        self.assertFalse(p['human_review_attested']);self.assertEqual(p['decisions'],[])

class PipelineIntegrationTests(unittest.TestCase):
    def test_review_run_rebuilds_exports_and_retains_original(self):
        import fitz
        import sqlite3
        from deallens.cli import run,load_latest,review_run
        project=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/'config').mkdir();(root/'data/sources').mkdir(parents=True)
            shutil.copytree(project/'deallens',root/'deallens',ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy2(project/'config/assumptions.json',root/'config/assumptions.json')
            (root/'config/sources.json').write_text(json.dumps([{'document_id':'synthetic_test','role':'development','url':'https://example.invalid/fixture.pdf'}]))
            pdf=fitz.open();p=pdf.new_page();p.insert_text((72,72),'Each share has the right to receive $22.00 in cash (the Merger Consideration).')
            pdf.save(root/'data/sources/synthetic_test.pdf');pdf.close()
            baseline=run(root)
            folder,manifest,bundles=load_latest(root)
            record=next(r for r in bundles[0]['extractions'] if r['field_name']=='consideration_per_share' and r['status']=='supported')
            submission={'base_run_id':baseline,'reviewer':'SYNTHETIC TEST ONLY','human_review_attested':True,
                        'decisions':[{'document_id':'synthetic_test','field_name':'consideration_per_share','document_layer':'8-k-summary',
                                      'action':'approve','record_ids':[record['record_id']],'reason':'Synthetic unit-test approval of the source amount.', 'complete_field_layer':True}]}
            before=(folder/'synthetic_test/extractions.json').read_bytes()
            # A correction cannot manufacture a new numeric value, even with attestation.
            bad=copy.deepcopy(submission);bad['decisions'][0].update(action='correct',normalized_value=23,currency='USD',value_qualifier='exact')
            with self.assertRaises(ValueError):review_run(root,bad)
            self.assertEqual(load_latest(root)[1]['run_id'],baseline)
            reviewed=review_run(root,submission)
            _,new_manifest,new_bundles=load_latest(root)
            self.assertEqual(new_manifest['parent_run_id'],baseline)
            self.assertEqual(before,(folder/'synthetic_test/extractions.json').read_bytes())
            self.assertEqual(new_bundles[0]['metrics']['human_verified_records'],1)
            self.assertIn('22.0',answer('consideration',new_bundles[0]['extractions'],new_bundles[0]['comparisons'],True)['answer'])
            with sqlite3.connect(root/'outputs/deallens.sqlite') as db:
                self.assertEqual(db.execute('SELECT COUNT(*) FROM runs').fetchone()[0],2)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM review_events').fetchone()[0],1)
            # Reusing a stale approval cannot create another run.
            with self.assertRaises(ValueError):review_run(root,submission)

if __name__=='__main__':unittest.main()
