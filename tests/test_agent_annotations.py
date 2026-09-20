import copy
import json
import tempfile
import unittest
from pathlib import Path
from deallens.assessments import annotate
from deallens.semantic import validate_proposals
from deallens.qa import answer, UNSUPPORTED
from deallens.extract import comparison
from test_semantic_review import fixture

class AnnotationTests(unittest.TestCase):
    def test_annotation_cannot_promote_candidate_or_verify_human(self):
        doc,req,p=fixture()
        records=validate_proposals({'proposals':[p]},req,doc,'r',.9)
        original=copy.deepcopy(records)
        note={k:records[0][k] for k in ('record_id','document_id','document_sha256','field_name')}
        note.update(human_review=False,assessment='Synthetic concern')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'data/assessments';folder.mkdir(parents=True)
            path=folder/'test.json';path.write_text(json.dumps({'records':[note]}))
            annotate(root,records)
            self.assertEqual(records[0]['status'],original[0]['status'])
            self.assertIsNone(records[0]['normalized_value'])
            self.assertNotEqual(records[0]['review_status'],'verified')
            self.assertEqual(answer('awards',records,comparison(records))['answer'],UNSUPPORTED)
            note['document_sha256']='changed';path.write_text(json.dumps({'records':[note]}))
            with self.assertRaises(ValueError):annotate(root,records)
