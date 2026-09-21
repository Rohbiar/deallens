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
from .semantic import extract_semantic,identify

def write_json(path,obj):
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")

def new_run_id():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+uuid.uuid4().hex[:8]

def derive_bundle(doc, records, assumptions, elapsed=0, model_audit=None, review_events=None):
    comparisons=comparison(records)
    b={"document":doc,"extractions":records,"comparisons":comparisons,"timeline":timeline(doc,records),
       "analytics":run_analytics(doc,records,comparisons,assumptions),"risk_map":risk_map(records),
       "qa":{k:answer(k,records,comparisons) for k in QUESTIONS},
       "exceptions":[r for r in records if r["review_status"]!="verified" and r["status"] not in {"superseded","rejected"}],
       "model_audit":model_audit or [],"review_events":review_events or []}
    active=[r for r in records if r["status"] not in {"superseded","rejected"}]
    supported={r["field_name"] for r in active if r["status"]=="supported"}
    b["metrics"]={"elapsed_seconds":round(elapsed,3),"page_count":doc["page_count"],"catalog_fields":len(FIELDS),
                  "machine_supported_fields":len(supported),
                  "source_excerpt_fields":len({r['field_name'] for r in active if r['status']=='source_excerpt'}),
                  "candidate_only_fields":len({r["field_name"] for r in active if r["status"]=="requires_review"}-supported),
                  "records":len(records),"evidence_exact_match_count":sum(bool(r.get("evidence")) for r in records),
                  "human_verified_records":sum(r["review_status"]=="verified" and r["status"]=="supported" for r in records),
                  "model_proposal_records":sum(r["extraction_method"]=="llm" for r in records),
                  "semantic_accuracy":None,"accuracy_note":"Citation substring validation is not extraction accuracy. No exhaustive human gold set."}
    return b

def persist(root,manifest,bundles,assumptions):
    folder=root/"outputs"/manifest["run_id"]
    folder.mkdir(parents=True,exist_ok=False)
    manifest["documents"]=[]
    for b in bundles:
        doc=b["document"];out=folder/doc["document_id"];out.mkdir()
        for k,value in b.items():write_json(out/(k+".json"),value)
        rows=b["analytics"].get("rows",[])
        with (out/"scenarios.csv").open("w",newline="") as f:
            if rows:
                writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        manifest["documents"].append({"document_id":doc["document_id"],"sha256":doc["sha256"],"metrics":b["metrics"]})
    write_json(folder/"assumptions.json",assumptions)
    write_json(folder/"manifest.json",manifest)
    save(root/"outputs/deallens.sqlite",manifest,bundles)
    pointer=root/"outputs"/(".latest-"+manifest["run_id"]+".json")
    write_json(pointer,{"run_id":manifest["run_id"]});pointer.replace(root/"outputs/latest.json")

def load_latest(root):
    latest=json.loads((root/"outputs/latest.json").read_text())["run_id"]
    if not latest or Path(latest).name!=latest:raise ValueError("Invalid run identifier")
    folder=root/"outputs"/latest
    manifest=json.loads((folder/"manifest.json").read_text())
    bundles=[]
    for item in manifest["documents"]:
        ident=item["document_id"]
        if not ident or Path(ident).name!=ident:raise ValueError("Invalid document identifier")
        out=folder/ident
        bundles.append({p.stem:json.loads(p.read_text()) for p in out.glob("*.json")})
    return folder,manifest,bundles

def review_run(root,submission):
    from .review import apply_decisions
    folder,manifest,bundles=load_latest(root)
    for b in bundles:
        doc=b["document"]
        if sha256((root/"data/sources"/doc["file_name"]).read_bytes())!=doc["sha256"]:
            raise ValueError("Source file changed since the reviewed run; reingest before approval")
        b["extractions"]=identify(b["extractions"])
    if (folder/"assumptions.json").exists():assumptions=json.loads((folder/"assumptions.json").read_text())
    else:
        path=root/"config/assumptions.json"
        if sha256(path.read_bytes())!=manifest["assumptions_sha256"]:raise ValueError("Original assumptions unavailable")
        assumptions=json.loads(path.read_text())
    run_id=new_run_id()
    revised,events=apply_decisions(manifest,bundles,submission,run_id)
    revised=[derive_bundle(b["document"],b["extractions"],assumptions,model_audit=b.get("model_audit"),review_events=b["review_events"]) for b in revised]
    updated={**manifest,"run_id":run_id,"parent_run_id":manifest["run_id"],"mode":"reviewed",
             "started_at":datetime.now(timezone.utc).isoformat(),"review_event_ids":[e["event_id"] for e in events]}
    updated["review_code_file_sha256"]={str(p.relative_to(root)):sha256(p.read_bytes()) for p in sorted((root/"deallens").glob("*.py"))}
    persist(root,updated,revised,assumptions)
    print("Reviewed run:",run_id)
    return run_id

def run(root,ids=None,threshold=0.9,model=None,model_fields=None,max_model_calls=12):
    configs=json.loads((root/"config/sources.json").read_text())
    if ids:configs=[s for s in configs if s["document_id"] in ids]
    if not configs:raise ValueError("No matching source documents")
    assumptions=json.loads((root/"config/assumptions.json").read_text())
    if not 0<=threshold<=1:raise ValueError("Invalid confidence threshold")
    provider=None
    if model:
        from .provider import OpenAIProvider
        from .budget import BudgetLedger
        provider=OpenAIProvider(budget=BudgetLedger(root/'outputs/api_budget.sqlite'))
    run_id=new_run_id()
    try:code=subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True,stderr=subprocess.DEVNULL).strip()
    except (OSError,subprocess.CalledProcessError):code="unversioned"
    manifest={"run_id":run_id,"started_at":datetime.now(timezone.utc).isoformat(),"code_version":code,
              "assumptions_version":assumptions["version"],"assumptions_sha256":sha256((root/"config/assumptions.json").read_bytes()),
              "mode":"hybrid_proposals" if model else "deterministic","model":model,"threshold":threshold,"documents":[],
              "model_budget_per_document":max_model_calls if model else 0}
    code_files=sorted((root/"deallens").glob("*.py"))+[root/"deallens/ui.html",root/"config/sources.json",root/"config/assumptions.json"]
    manifest["code_file_sha256"]={str(p.relative_to(root)):sha256(p.read_bytes()) for p in code_files}
    manifest["assessment_file_sha256"]={str(p.relative_to(root)):sha256(p.read_bytes()) for p in sorted((root/"data/assessments").glob("*.json"))}
    bundles=[]
    for source in configs:
        start=time.perf_counter();path=root/"data/sources"/(source["document_id"]+".pdf")
        if not path.exists():download(source["url"],path)
        doc=ingest(path,source);records=extract(doc,run_id,threshold);model_audit=[]
        if provider:
            proposed,model_audit=extract_semantic(doc,run_id,provider,model,fields=model_fields,threshold=threshold,max_calls=max_model_calls,
                progress=lambda field,layer,status: print(f"{source['document_id']} / {field} / {layer}: {status}",flush=True))
            records.extend(proposed)
            for entry in model_audit:
                if entry['status']=='provider_error':
                    print(f"WARNING {source['document_id']}: {entry['error']} Offline results will still be saved; this is not successful live extraction.")
        from .assessments import annotate
        records=annotate(root,identify(records))
        from .provisions import all_evidence
        for r in records:
            if r.get("evidence") and not all(validate_evidence(s,doc) for s in all_evidence(r)):raise ValueError("Internal evidence mismatch")
        b=derive_bundle(doc,records,assumptions,time.perf_counter()-start,model_audit=model_audit)
        bundles.append(b)
        print(source["document_id"],json.dumps(b["metrics"]))
    hashes=[b["document"]["sha256"] for b in bundles]
    if len(hashes)!=len(set(hashes)):raise ValueError("Duplicate source documents in this run")
    if provider:
        manifest['api_budget'] = provider.budget.summary()
        print('API budget:',json.dumps(manifest['api_budget']))
    persist(root,manifest,bundles,assumptions)
    print("Run:",run_id)
    return run_id

def main():
    p=argparse.ArgumentParser(description="DealLens public-source research prototype")
    p.add_argument("--root",type=Path,default=Path.cwd())
    sub=p.add_subparsers(dest="command",required=True)
    r=sub.add_parser("run");r.add_argument("--documents",nargs="+");r.add_argument("--threshold",type=float,default=.9)
    r.add_argument("--model",help="Optional OpenAI model identifier; requires local OPENAI_API_KEY")
    r.add_argument("--model-fields",nargs="+",choices=list(FIELDS));r.add_argument("--max-model-calls",type=int,default=12)
    sub.add_parser("refresh",help="Re-run offline rules and retain historical unverified model proposals; no API calls")
    e=sub.add_parser("review-export");e.add_argument("--out",type=Path,required=True)
    a=sub.add_parser("review-apply");a.add_argument("packet",type=Path)
    q=sub.add_parser("ask");q.add_argument("document");q.add_argument("question");q.add_argument("--strict",action="store_true")
    s=sub.add_parser("serve");s.add_argument("--port",type=int,default=8765)
    args=p.parse_args();root=args.root.resolve()
    if args.command=="run":run(root,args.documents,args.threshold,args.model,args.model_fields,args.max_model_calls)
    elif args.command=="refresh":
        from .reprocess import reprocess
        reprocess(root)
    elif args.command=="review-export":
        from .review import packet
        _,manifest,bundles=load_latest(root)
        for b in bundles:b["extractions"]=identify(b["extractions"])
        if args.out.exists():raise ValueError("Review export path already exists; choose a new filename to preserve edits")
        write_json(args.out,packet(manifest,bundles));print("Review packet:",args.out)
    elif args.command=="review-apply":review_run(root,json.loads(args.packet.read_text()))
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
