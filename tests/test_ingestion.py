import tempfile
from pathlib import Path
import unittest
import fitz
from deallens.ingest import ingest
from deallens.extract import extract

class IngestionTests(unittest.TestCase):
    def make_pdf(self,path,contents):
        doc=fitz.open()
        for text in contents:
            p=doc.new_page();p.insert_text((72,72),text)
        doc.save(path);doc.close()
    def test_duplicate_and_sparse_pages_flagged(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.pdf';self.make_pdf(path,['A machine readable paragraph repeated across two document pages.']*2+[''])
            d=ingest(path,{'document_id':'x','url':'https://example.invalid/x.pdf'})
            kinds={w['type'] for w in d['warnings']}
            self.assertIn('duplicate_page_text',kinds);self.assertIn('unreadable_or_sparse_page',kinds)
            self.assertIsNone(d['filing_date']);self.assertTrue(d['ocr_required'])
    def test_expected_page_count_detects_missing_page(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.pdf';self.make_pdf(path,['One page of source material with sufficient text.'])
            with self.assertRaises(ValueError):ingest(path,{'document_id':'x','url':'https://example.invalid/x.pdf','expected_page_count':2})
    def test_source_pin_detects_modified_document(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.pdf';self.make_pdf(path,['Source material which is not the pinned original.'])
            with self.assertRaises(ValueError):ingest(path,{'document_id':'x','url':'https://example.invalid/x.pdf','expected_sha256':'invalid'})
    def test_threshold_blocks_scalar_normalization(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'x.pdf';self.make_pdf(path,['Each share has the right to receive $22.00 in cash (the Merger Consideration).'])
            d=ingest(path,{'document_id':'x','url':'https://example.invalid/x.pdf'})
            rows=extract(d,'test',.99)
            self.assertFalse(any(r['status']=='supported' for r in rows))
            self.assertTrue(any(r['status']=='low_confidence' for r in rows))

if __name__=='__main__':unittest.main()
