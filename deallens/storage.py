"""Append-only run lineage with queryable SQLite evidence and outputs."""
import json
import sqlite3

SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS runs(run_id TEXT PRIMARY KEY, started_at TEXT, code_version TEXT, assumptions_version TEXT);
CREATE TABLE IF NOT EXISTS documents(run_id TEXT, document_id TEXT, sha256 TEXT, source_url TEXT, page_count INTEGER, metadata_json TEXT,
 PRIMARY KEY(run_id,document_id), FOREIGN KEY(run_id) REFERENCES runs(run_id));
CREATE TABLE IF NOT EXISTS pages(run_id TEXT, document_id TEXT, page INTEGER, document_layer TEXT, text_sha256 TEXT, text TEXT,
 PRIMARY KEY(run_id,document_id,page), FOREIGN KEY(run_id,document_id) REFERENCES documents(run_id,document_id));
CREATE TABLE IF NOT EXISTS fields(id INTEGER PRIMARY KEY, run_id TEXT, document_id TEXT, field_name TEXT, document_layer TEXT, status TEXT,
 normalized_value TEXT, confidence REAL, review_status TEXT, page INTEGER, record_json TEXT,
 FOREIGN KEY(run_id,document_id) REFERENCES documents(run_id,document_id));
CREATE TABLE IF NOT EXISTS comparisons(run_id TEXT, document_id TEXT, field_name TEXT, classification TEXT, record_json TEXT,
 PRIMARY KEY(run_id,document_id,field_name), FOREIGN KEY(run_id,document_id) REFERENCES documents(run_id,document_id));
CREATE TABLE IF NOT EXISTS scenarios(run_id TEXT, document_id TEXT, scenario_id TEXT, strategy TEXT, currency TEXT, net_cost REAL, record_json TEXT,
 PRIMARY KEY(run_id,document_id,scenario_id,strategy), FOREIGN KEY(run_id,document_id) REFERENCES documents(run_id,document_id));
CREATE INDEX IF NOT EXISTS fields_lookup ON fields(run_id,document_id,field_name,status);
CREATE TABLE IF NOT EXISTS review_events(event_id TEXT PRIMARY KEY, run_id TEXT, document_id TEXT, reviewer TEXT, record_json TEXT);
CREATE TABLE IF NOT EXISTS model_requests(run_id TEXT, document_id TEXT, request_index INTEGER, status TEXT, record_json TEXT,
 PRIMARY KEY(run_id,document_id,request_index));
CREATE TABLE IF NOT EXISTS structured_terms(term_id TEXT, run_id TEXT, document_id TEXT,
 field_name TEXT, document_layer TEXT, status TEXT, review_status TEXT, record_json TEXT,
 PRIMARY KEY(run_id,document_id,term_id),
 FOREIGN KEY(run_id,document_id) REFERENCES documents(run_id,document_id));
CREATE INDEX IF NOT EXISTS structured_terms_lookup ON structured_terms(run_id,document_id,field_name,status);
DROP VIEW IF EXISTS review_queue;
CREATE VIEW review_queue AS SELECT run_id,document_id,field_name,document_layer,status,review_status,page,record_json
 FROM fields WHERE review_status <> 'verified' AND status NOT IN ('superseded','rejected');
"""

def save(path,manifest,bundles):
    with sqlite3.connect(path) as db:
        db.executescript(SCHEMA)
        db.execute("INSERT INTO runs VALUES(?,?,?,?)",(manifest["run_id"],manifest["started_at"],manifest["code_version"],manifest["assumptions_version"]))
        for b in bundles:
            d=b["document"];run=manifest["run_id"];ident=d["document_id"]
            db.execute("INSERT INTO documents VALUES(?,?,?,?,?,?)",(run,ident,d["sha256"],d["url"],d["page_count"],json.dumps({k:v for k,v in d.items() if k not in {"pages","chunks"}})))
            db.executemany("INSERT INTO pages VALUES(?,?,?,?,?,?)",[(run,ident,p["page"],p["document_layer"],p["text_sha256"],p["text"]) for p in d["pages"]])
            db.executemany("INSERT INTO fields(run_id,document_id,field_name,document_layer,status,normalized_value,confidence,review_status,page,record_json) VALUES(?,?,?,?,?,?,?,?,?,?)",[(run,ident,r["field_name"],r["document_layer"],r["status"],json.dumps(r["normalized_value"]),r["confidence"],r["review_status"],r["page"],json.dumps(r)) for r in b["extractions"]])
            db.executemany("INSERT INTO comparisons VALUES(?,?,?,?,?)",[(run,ident,c["field_name"],c["classification"],json.dumps(c)) for c in b["comparisons"]])
            db.executemany("INSERT INTO scenarios VALUES(?,?,?,?,?,?,?)",[(run,ident,r["scenario_id"],r["strategy"],r["currency"],r["net_incremental_cost_pv"],json.dumps(r)) for r in b["analytics"].get("rows",[])])
            for event in b.get("review_events",[]):
                db.execute("INSERT OR IGNORE INTO review_events VALUES(?,?,?,?,?)",(event["event_id"],event["new_run_id"],ident,event["reviewer"],json.dumps(event)))
            db.executemany("INSERT INTO model_requests VALUES(?,?,?,?,?)",[(run,ident,i,r["status"],json.dumps(r)) for i,r in enumerate(b.get("model_audit",[]))])
            db.executemany("INSERT INTO structured_terms VALUES(?,?,?,?,?,?,?,?)",[
                (term["term_id"],run,ident,term["field_name"],term.get("document_layer"),
                 term["status"],term.get("review_status","unreviewed"),json.dumps(term))
                for term in b.get("structured_terms",[])])
