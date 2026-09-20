import json
import tempfile
import unittest
from pathlib import Path
from deallens.server import run_snapshot, source_is_current
from deallens.ingest import sha256

class SnapshotTests(unittest.TestCase):
    def test_refresh_and_explicit_pin(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);out=root/'outputs';out.mkdir()
            for run in ['old','new']:
                (out/run).mkdir()
                (out/run/'manifest.json').write_text(json.dumps({'run_id':run,'documents':[{'document_id':run}]}))
            (out/'latest.json').write_text('{"run_id":"old"}')
            self.assertEqual(run_snapshot(root)[1]['run_id'],'old')
            (out/'latest.json').write_text('{"run_id":"new"}')
            self.assertEqual(run_snapshot(root)[1]['run_id'],'new')
            self.assertEqual(run_snapshot(root,'old')[1]['run_id'],'old')
            for invalid in ['../old','..','/tmp/old']:
                with self.assertRaises(ValueError):run_snapshot(root,invalid)

    def test_modified_or_missing_original_is_stale(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);folder=root/'data/sources';folder.mkdir(parents=True)
            path=folder/'demo.pdf';path.write_bytes(b'original')
            manifest={'documents':[{'document_id':'demo','sha256':sha256(b'original')}]}
            self.assertTrue(source_is_current(root,manifest,'demo'))
            path.write_bytes(b'replacement')
            self.assertFalse(source_is_current(root,manifest,'demo'))
            path.unlink()
            self.assertFalse(source_is_current(root,manifest,'demo'))
