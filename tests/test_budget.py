import io
import json
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from deallens.budget import BudgetLedger, CAP_MICRO_USD
from deallens.provider import OpenAIProvider, ProviderError


class BudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/'budget.sqlite'
        self.ledger = BudgetLedger(self.path)
        self.body = {'model':'gpt-4.1-mini','max_output_tokens':6000,'input':'test'}

    def tearDown(self):
        self.temp.cleanup()

    def test_reservations_survive_restarts_and_usage_does_not_refund(self):
        rid = self.ledger.reserve(self.body)
        before = self.ledger.summary()
        self.ledger.record_usage(rid, {'input_tokens':1,'output_tokens':1})
        self.assertEqual(BudgetLedger(self.path).summary(), before)
        self.assertGreater(before['reserved_usd'], 1)

    def test_rejects_unpriced_models_tools_and_oversize_requests(self):
        for change in [{'model':'unknown'}, {'tools':[{'type':'web_search'}]}, {'input':'x'*150001}, {'max_output_tokens':10000}]:
            with self.subTest(change=list(change)), self.assertRaises(ProviderError):
                self.ledger.reserve({**self.body, **change})
        self.assertEqual(self.ledger.summary()['attempts'],0)

    def test_cap_survives_concurrent_attempts(self):
        rid = self.ledger.reserve(self.body)
        with sqlite3.connect(self.path) as db:
            amount = db.execute('SELECT reserved_micro_usd FROM reservations WHERE id=?',(rid,)).fetchone()[0]
            db.execute('DELETE FROM reservations WHERE id=?',(rid,))
            db.execute('UPDATE reservations SET reserved_micro_usd=? WHERE id=0',(CAP_MICRO_USD-amount,))
        def attempt(_):
            try: self.ledger.reserve(self.body); return True
            except ProviderError: return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(attempt,range(2))),1)
        self.assertEqual(self.ledger.summary()['reserved_usd'],10)

    def test_each_http_retry_reserves_before_transport(self):
        calls=[]
        def opener(*args,**kwargs):
            calls.append(self.ledger.summary()['attempts'])
            if len(calls)<3: raise HTTPError('https://example.invalid',429,'test',{},None)
            return io.BytesIO(json.dumps({'status':'completed','usage':{'input_tokens':1,'output_tokens':1},
                'output':[{'content':[{'type':'output_text','text':'{"proposals":[]}'}]}]}).encode())
        provider=OpenAIProvider('synthetic',opener=opener,sleeper=lambda _:None,budget=self.ledger)
        provider({'model':'gpt-4.1-mini','system':'test','chunks':[]})
        self.assertEqual(calls,[1,2,3])

    def test_exhausted_budget_never_calls_transport(self):
        with sqlite3.connect(self.path) as db:
            db.execute('UPDATE reservations SET reserved_micro_usd=? WHERE id=0',(CAP_MICRO_USD,))
        calls=[]
        provider=OpenAIProvider('synthetic',opener=lambda *a,**k:calls.append(1),budget=self.ledger)
        with self.assertRaises(ProviderError):provider({'model':'gpt-4.1-mini','system':'test','chunks':[]})
        self.assertEqual(calls,[])
