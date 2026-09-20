"""Read-only, loopback-only research UI; no trade or external model tools."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
from urllib.parse import urlparse,parse_qs
from .qa import answer

def serve(root,port):
    run_id=json.loads((root/"outputs/latest.json").read_text())["run_id"]
    folder=root/"outputs"/run_id
    manifest=json.loads((folder/"manifest.json").read_text())
    ids={d["document_id"] for d in manifest["documents"]}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url=urlparse(self.path);parts=url.path.strip("/").split("/")
            status=200;ctype="application/json; charset=utf-8"
            if url.path=="/":
                data=(Path(__file__).parent/"ui.html").read_bytes();ctype="text/html; charset=utf-8"
            elif url.path=="/api/manifest":data=json.dumps(manifest).encode()
            elif len(parts)==2 and parts[0]=="api" and parts[1] in ids:
                p=folder/parts[1]
                b={k:json.loads((p/(k+".json")).read_text()) for k in ("document","extractions","comparisons","timeline","analytics","metrics")}
                data=json.dumps(b).encode()
            elif len(parts)==2 and parts[0]=="source" and parts[1] in ids:
                data=(root/"data/sources"/(parts[1]+".pdf")).read_bytes();ctype="application/pdf"
            elif len(parts)==2 and parts[0]=="ask" and parts[1] in ids:
                p=folder/parts[1];q=parse_qs(url.query).get("q",[""])[0][:1000]
                result=answer(q,json.loads((p/"extractions.json").read_text()),json.loads((p/"comparisons.json").read_text()),parse_qs(url.query).get("strict",["false"])[0]=="true")
                data=json.dumps(result).encode()
            else:status=404;data=b'{"error":"not found"}'
            self.send_response(status);self.send_header("Content-Type",ctype)
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
            self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(data)
        def log_message(self,*args):pass
    print(f"DealLens: http://127.0.0.1:{port} (read-only public-source research)",flush=True)
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
