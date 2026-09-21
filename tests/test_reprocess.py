import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from deallens.ingest import sha256
from deallens.reprocess import reprocess
from deallens.semantic import validate_proposals
from test_semantic_review import fixture

class ReprocessTests(unittest.TestCase):
    def test_preserves_paid_proposals_without_human_promotion(self):
        doc,req,p=fixture()
        doc['file_name']='demo.pdf';doc['sha256']=sha256(b'original bytes')
        records=validate_proposals({'proposals':[p]},req,doc,'base',.9)
        bundles=[{'document':doc,'extractions':records,'model_audit':[{'status':'proposals_retained'}]}]
        original=copy.deepcopy(bundles)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'data/sources').mkdir(parents=True)
            (root/'data/sources/demo.pdf').write_bytes(b'original bytes')
            (root/'assumptions.json').write_text('{}')
            with patch('deallens.cli.load_latest',return_value=(root,{'run_id':'base'},bundles)), patch('deallens.cli.persist') as persist, patch('deallens.cli.derive_bundle',side_effect=lambda d,r,a,**kw:{'extractions':r,**kw}):
                reprocess(root)
                updated=persist.call_args.args[1];revised=persist.call_args.args[2]
                candidate=next(r for r in revised[0]['extractions'] if r['extraction_method']=='llm')
                self.assertEqual(updated['new_provider_calls'],0)
                self.assertEqual(updated['parent_run_id'],'base')
                self.assertEqual(candidate['origin_run_id'],'base')
                self.assertIsNone(candidate['normalized_value'])
                self.assertEqual(revised[0]['model_audit'][0]['origin_run_id'],'base')
                self.assertEqual(bundles,original)
                bundles[0]['extractions'][0]['review_status']='verified'
                with self.assertRaises(ValueError):reprocess(root)

    def test_consolidation_preserves_document_origins_and_rejects_assumption_mismatch(self):
        doc,req,p=fixture();doc['file_name']='demo.pdf';doc['sha256']=sha256(b'original bytes')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'data/sources').mkdir(parents=True)
            (root/'data/sources/demo.pdf').write_bytes(b'original bytes')
            selection={}
            for ident,origin in [('first','base1'),('second','base2')]:
                folder=root/'outputs'/origin;out=folder/ident;out.mkdir(parents=True)
                copydoc={**doc,'document_id':ident}
                (out/'document.json').write_text(json.dumps(copydoc))
                (out/'extractions.json').write_text('[]')
                (out/'model_audit.json').write_text('[{"status":"abstained"}]')
                (folder/'assumptions.json').write_text('{}')
                (folder/'manifest.json').write_text(json.dumps({'run_id':origin,'documents':[{'document_id':ident}]}))
                selection[ident]=origin
            with patch('deallens.cli.load_latest',return_value=(root,{},[])), patch('deallens.cli.persist') as persist, patch('deallens.cli.derive_bundle',side_effect=lambda d,r,a,**kw:{'document':d,'extractions':r,**kw}):
                reprocess(root,selection)
                manifest,bundles=persist.call_args.args[1:3]
                self.assertEqual(manifest['source_runs'],selection)
                self.assertEqual(manifest['new_provider_calls'],0)
                self.assertEqual([b['model_audit'][0]['origin_run_id'] for b in bundles],['base1','base2'])
                (root/'outputs/base2/assumptions.json').write_text('{"changed":true}')
                with self.assertRaisesRegex(ValueError,'different assumptions'):reprocess(root,selection)
