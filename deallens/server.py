"""Read-only, loopback-only research UI; no trade or external model tools."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from urllib.parse import urlparse,parse_qs
from .qa import answer, UNSUPPORTED
from .ingest import sha256

def run_snapshot(root, requested_run=None):
    run_id=requested_run or json.loads((root/"outputs/latest.json").read_text())["run_id"]
    if not run_id or Path(run_id).name != run_id or run_id in {".",".."}:
        raise ValueError("Invalid run identifier")
    folder=root/"outputs"/run_id
    manifest=json.loads((folder/"manifest.json").read_text())
    return folder, manifest, {d["document_id"] for d in manifest["documents"]}

def source_is_current(root, manifest, ident):
    expected=next(d['sha256'] for d in manifest['documents'] if d['document_id']==ident)
    try:
        return sha256((root/'data/sources'/(ident+'.pdf')).read_bytes())==expected
    except OSError:
        return False


def serve(root,port):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url=urlparse(self.path);parts=url.path.strip("/").split("/")
            try:
                folder,manifest,ids=run_snapshot(root,parse_qs(url.query).get("run",[None])[0])
            except (ValueError, OSError):
                self.send_error(404,"Run not found");return
            status=200;ctype="application/json; charset=utf-8"
            if url.path=="/":
                data=(Path(__file__).parent/"ui.html").read_bytes();ctype="text/html; charset=utf-8"
            elif url.path=="/api/manifest":data=json.dumps(manifest).encode()
            elif url.path=="/api/review-packet":
                from .review import packet
                from .semantic import identify
                bundles=[]
                for ident in sorted(ids):
                    p=folder/ident
                    bundles.append({"document":{"document_id":ident},"extractions":identify(json.loads((p/"extractions.json").read_text()))})
                data=json.dumps(packet(manifest,bundles),indent=2).encode()
            elif len(parts)==2 and parts[0]=="api" and parts[1] in ids:
                p=folder/parts[1]
                b={k:json.loads((p/(k+".json")).read_text()) for k in ("document","extractions","comparisons","timeline","risk_map","analytics","metrics")}
                for k in ("model_audit","review_events"):
                    if (p/(k+".json")).exists():b[k]=json.loads((p/(k+".json")).read_text())
                b["stale_source"]=not source_is_current(root,manifest,parts[1])
                b["run_manifest"]=manifest
                data=json.dumps(b).encode()
            elif len(parts)==2 and parts[0]=="source" and parts[1] in ids:
                if not source_is_current(root,manifest,parts[1]):
                    status=409;data=b'{"error":"Source differs from this run; reingest before viewing evidence"}'
                else:
                    data=(root/"data/sources"/(parts[1]+".pdf")).read_bytes();ctype="application/pdf"
            elif len(parts)==2 and parts[0]=="ask" and parts[1] in ids:
                p=folder/parts[1];q=parse_qs(url.query).get("q",[""])[0][:1000]
                result=answer(q,json.loads((p/"extractions.json").read_text()),json.loads((p/"comparisons.json").read_text()),parse_qs(url.query).get("strict",["false"])[0]=="true")
                if not source_is_current(root,manifest,parts[1]):
                    result={"question":q,"answer":UNSUPPORTED,"status":"stale_input","designation":"analysis","sources":[],"note":"Source bytes differ from this run; reingest before relying on this answer."}
                result["run_id"]=manifest["run_id"]
                data=json.dumps(result).encode()
            else:status=404;data=b'{"error":"not found"}'
            self.send_response(status);self.send_header("Content-Type",ctype)
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
            self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(data)
        def log_message(self,*args):pass
    print(f"DealLens: http://127.0.0.1:{port} (read-only public-source research)",flush=True)
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
