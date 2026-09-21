"""Persistent conservative reservations for the user's $10 testing allowance.

Not an account billing limit: applies to this project's CLI only. Reservations
are never refunded automatically, including failures, crashes and retries.
"""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from .provider import ProviderError, GPT55_MODELS

CAP_MICRO_USD = 10_000_000
HISTORICAL_BUFFER_MICRO_USD = 1_000_000
MINI_MODELS = {'gpt-4.1-mini', 'gpt-4.1-mini-2025-04-14'}
MODELS = MINI_MODELS | GPT55_MODELS
PRICE_SOURCES = {m: 'https://developers.openai.com/api/docs/models/' + ('gpt-5.5' if m in GPT55_MODELS else 'gpt-4.1-mini') for m in MODELS}
PRICE_SOURCE = 'https://developers.openai.com/api/docs/models/gpt-4.1-mini'


class BudgetLedger:
    def __init__(self, path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS reservations (id INTEGER PRIMARY KEY, created_at TEXT, request_sha256 TEXT, reserved_micro_usd INTEGER NOT NULL, usage_json TEXT)')
            db.execute('INSERT OR IGNORE INTO reservations VALUES (0, ?, ?, ?, NULL)',
                       (datetime.now(timezone.utc).isoformat(), 'historical-and-billing-buffer', HISTORICAL_BUFFER_MICRO_USD))

    @staticmethod
    def estimate_micro_usd(body):
        if body.get('model') not in MODELS:
            raise ProviderError('Budget guard has no approved price for this model; no request sent.')
        if body.get('tools') or body.get('max_output_tokens') != 6000:
            raise ProviderError('Budget guard only supports tool-free requests capped at 6000 output tokens.')
        encoded = json.dumps(body, ensure_ascii=False).encode()
        if len(encoded) > 150_000:
            raise ProviderError('Request exceeds budget guard input size limit; no request sent.')
        # Input byte count exceeds ordinary text token count; add schema/framing
        # overhead, then double the price estimate. Never assume cache discounts.
        # Verified 2026-09-20: mini $0.40/$1.60; GPT-5.5 $5/$30 per million.
        tokens = len(encoded) + 8192
        input_rate, output_rate = (50, 300) if body["model"] in GPT55_MODELS else (4, 16)
        return (2 * (tokens * input_rate + 6000 * output_rate) + 9) // 10

    def reserve(self, body):
        reserve = self.estimate_micro_usd(body)
        encoded = json.dumps(body, ensure_ascii=False).encode()
        with sqlite3.connect(self.path, timeout=30) as db:
            db.execute('BEGIN IMMEDIATE')
            used = db.execute('SELECT COALESCE(SUM(reserved_micro_usd),0) FROM reservations').fetchone()[0]
            if used + reserve > CAP_MICRO_USD:
                raise ProviderError('Persistent $10 API testing allowance reached; no request sent. Do not reset the ledger without new authorization.')
            cursor = db.execute('INSERT INTO reservations (created_at,request_sha256,reserved_micro_usd) VALUES (?,?,?)',
                                (datetime.now(timezone.utc).isoformat(), hashlib.sha256(encoded).hexdigest(), reserve))
            return cursor.lastrowid

    def record_usage(self, reservation_id, usage):
        with sqlite3.connect(self.path) as db:
            db.execute('UPDATE reservations SET usage_json=? WHERE id=?',
                       (json.dumps(usage), reservation_id))

    def summary(self):
        with sqlite3.connect(self.path) as db:
            used, attempts = db.execute('SELECT SUM(reserved_micro_usd),COUNT(*)-1 FROM reservations').fetchone()
        return {'cap_usd':10, 'historical_buffer_usd':1, 'reserved_usd':used/1e6,
                'remaining_reservation_usd':(CAP_MICRO_USD-used)/1e6, 'attempts':attempts,
                'price_source':PRICE_SOURCE, 'price_sources':PRICE_SOURCES, 'price_checked':'2026-09-20',
                'note':'Conservative local reservations, not billed spend. Each retry charged to allowance; failures never auto-refunded. Excludes other apps, taxes and price changes.'}
