from __future__ import annotations
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import time
import uuid
from .ingest import ingest,download,sha256
from .extract import extract,comparison,timeline,validate_evidence
from .analytics import run_analytics
from .qa import answer
from .catalog import FIELDS,QUESTIONS
from .storage import save
from .risk import risk_map

def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")

def run(root,ids=None,threshold=0.9):
    configs=json.loads((root/"config/sources.json").read_text())
    if ids:configs=[s for s in configs if s["document_id"] in ids]
    if not configs:raise ValueError("No matching source documents")
    assumptions=json.loads((root/"config/assumptions.json").read_text())
    run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8]
    folder=root/"outputs"/run_id;folder.mkdir(parents=True)
    try:code=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):code="unversioned"
    manifest={"run_id":run_id,"started_at":datetime.now(timezone.utc).isoformat(),"code_version":code,
              "assumptions_version":assumptions["version"],"assumptions_sha256":sha256((root/"config/assumptions.json").read_bytes()),
              "mode":"deterministic","model":None,"threshold":threshold,"documents":[]}
    bundles=[]
    for source in configs:
        start=time.perf_counter();path=root/"data/sources"/(source["document_id"]+".pdf")
        if not path.exists():download(source["url"],path)
        doc=ingest(path,source);records=extract(doc,run_id,threshold)
        for r in records:
            if r.get("evidence") and not validate_evidence(r,doc):raise ValueError("Internal evidence mismatch")
        comparisons=comparison(records)
        b={"document":doc,"extractions":records,"comparisons":comparisons,"timeline":timeline(doc,records),
           "analytics":run_analytics(doc,records,comparisons,assumptions)}
        b["risk_map"]=risk_map(records)
        b["qa"]={k:answer(k,records,comparisons) for k in QUESTIONS}
        b["exceptions"]=[r for r in records if r["review_status"]!="verified"]
        b["metrics"]={"elapsed_seconds":round(time.perf_counter()-start,3),"page_count":doc["page_count"],
                       "catalog_fields":len(FIELDS),"machine_supported_fields":len({r["field_name"] for r in records if r["status"]=="supported"}),
                       "candidate_only_fields":len({r["field_name"] for r in records if r["status"]=="requires_review"}-{r["field_name"] for r in records if r["status"]=="supported"}),
                       "records":len(records),"evidence_exact_match_count":sum(bool(r.get('evidence')) for r in records),
                       "human_verified_records":0,"semantic_accuracy":None,
                       "accuracy_note":"Citation substring validation is not extraction accuracy. No exhaustive human gold set."}
        bundles.append(b);out=folder/source["document_id"];out.mkdir()
        for k in ["extractions","comparisons","timeline","risk_map","analytics","qa","exceptions","metrics"]:write_json(out/(k+".json"),b[k])
        write_json(out/"document.json",doc)
        with (out/"scenarios.csv").open("w",newline="") as f:
            rows=b["analytics"].get("rows",[])
            if rows:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        manifest["documents"].append({"document_id":source["document_id"],"sha256":doc["sha256"],"metrics":b["metrics"]})
        print(source["document_id"],json.dumps(b["metrics"]))
    hashes=[b["document"]["sha256"] for b in bundles]
    if len(hashes)!=len(set(hashes)):raise ValueError("Duplicate source documents in this run")
    save(root/"outputs/deallens.sqlite",manifest,bundles)
    write_json(folder/"manifest.json",manifest)
    write_json(root/"outputs/latest.json",{"run_id":run_id})
    print("Run:",run_id)
    return run_id

def main():
    p=argparse.ArgumentParser(description="DealLens public-source research prototype")
    p.add_argument("--root",type=Path,default=Path.cwd())
    sub=p.add_subparsers(dest="command",required=True)
    r=sub.add_parser("run");r.add_argument("--documents",nargs="+");r.add_argument("--threshold",type=float,default=.9)
    q=sub.add_parser("ask");q.add_argument("document");q.add_argument("question");q.add_argument("--strict",action="store_true")
    s=sub.add_parser("serve");s.add_argument("--port",type=int,default=8765)
    args=p.parse_args();root=args.root.resolve()
    if args.command=="run":run(root,args.documents,args.threshold)
    elif args.command=="serve":
        from .server import serve
        serve(root,args.port)
    else:
        latest=json.loads((root/"outputs/latest.json").read_text())["run_id"]
        manifest=json.loads((root/"outputs"/latest/"manifest.json").read_text())
        if args.document not in {d["document_id"] for d in manifest["documents"]}:p.error("Unknown document")
        path=root/"outputs"/latest/args.document
        print(json.dumps(answer(args.question,json.loads((path/"extractions.json").read_text()),json.loads((path/"comparisons.json").read_text()),args.strict),indent=2,ensure_ascii=False))

if __name__=="__main__":main()
