"""PDF ingestion. No document-provided instruction is ever executed."""
from __future__ import annotations
import hashlib
import re
import unicodedata
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import fitz

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def download(url: str, destination: Path) -> None:
    if not url.startswith("https://"):
        raise ValueError("Only HTTPS source URLs are supported")
    with urllib.request.urlopen(url, timeout=45) as response:
        data = response.read(40_000_001)
    if len(data) > 40_000_000 or not data.startswith(b"%PDF"):
        raise ValueError("Invalid PDF or source exceeds 40 MB limit")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)

def ingest(path: Path, source: dict) -> dict:
    data = path.read_bytes()
    if not data.startswith(b"%PDF"):
        raise ValueError("Source is not a PDF")
    checksum = sha256(data)
    if source.get("expected_sha256") and source["expected_sha256"] != checksum:
        raise ValueError("Source checksum differs from pinned source manifest")
    pages, warnings, seen = [], [], {}
    layer, exhibit = "8-k-summary", None
    with fitz.open(stream=data, filetype="pdf") as pdf:
        if pdf.needs_pass or len(pdf) == 0:
            raise ValueError("Encrypted or empty PDF")
        for index, page in enumerate(pdf):
            raw = page.get_text(sort=True)
            text = normalize(raw)
            header = re.search(r"(?im)^\s*Exhibit\s+(\d+\.\d+)\s*$", raw[:750])
            if header:
                exhibit = header.group(1)
                if exhibit.startswith("2."):
                    layer = "transaction-agreement"
                elif re.search(r"BRIDGE\s+CREDIT\s+AGREEMENT|CREDIT\s+AGREEMENT", text[:1500], re.I):
                    layer = "financing-agreement"
                else:
                    layer = "other-exhibit"
            digest = sha256(text.encode())
            readable = len(re.sub(r"\W", "", text)) >= 30
            if not readable:
                warnings.append({"type":"unreadable_or_sparse_page", "page":index+1,
                                 "action":"Inspect page; OCR may be required. Extraction blocked for this page."})
            if digest in seen and text:
                warnings.append({"type":"duplicate_page_text", "page":index+1, "same_as":seen[digest]})
            seen[digest] = index+1
            pages.append({"page":index+1,"text":text,"raw_text":raw,"text_sha256":digest,
                          "document_layer":layer,"exhibit":exhibit,"machine_readable":readable,
                          "locator":f"{source['document_id']}:{checksum[:12]}:p{index+1}"})
    head = " ".join(p["text"] for p in pages[:5])
    if re.search(r"voluntary public takeover offer", head, re.I):
        structure = "public_takeover_offer"
    elif re.search(r"will merge with and into|merge with and into", head, re.I):
        structure = "merger"
    else:
        structure = "unresolved"
    # Filing date is not the date of earliest event or agreement/signature date.
    filing = source.get("filing_date")
    if source.get("expected_page_count") is None or not source.get("inventory_source"):
        warnings.append({"type":"completeness_unverified", "action":"No externally checked page inventory supplied; internal page continuity is not proof of completeness."})
    else:
        warnings.append({"type":"publisher_snapshot_checked", "action":"Page count and bytes checked against a fresh publisher download. This does not establish completeness of omitted schedules or incorporated documents."})
    if source.get("expected_page_count") is not None and source["expected_page_count"]!=len(pages):
        raise ValueError("Missing or extra pages relative to expected source inventory")
    warnings.append({"type":"source_freshness_unverified", "action":"Snapshot of supplied filing only; later amendments, deal status and market inputs have not been checked."})
    if filing is None or source.get('filing_date_status') == 'pdf_metadata_reported':
        warnings.append({"type":"filing_date_not_verified", "action":"Obtain filing index metadata; do not substitute event or signing date."})
    if not any(p["document_layer"]=="transaction-agreement" for p in pages):
        warnings.append({"type":"missing_agreement_exhibit"})
    report = re.search(r"Date of Report.*?:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})", head)
    chunks = []
    for page in pages:
        if not page["machine_readable"]:
            continue
        for start in range(0, len(page["text"]), 1300):
            end = min(start+1800, len(page["text"]))
            chunks.append({"chunk_id":f"{page['locator']}:c{start}-{end}","page":page["page"],
                           "document_layer":page["document_layer"],"start":start,"end":end,
                           "text":page["text"][start:end]})
    return {**source,"sha256":checksum,"version":checksum,"file_name":path.name,
            "filing_date":filing,"filing_date_status":source.get('filing_date_status',"provided" if filing else "not_found"),
            "report_event_date_raw":report.group(1) if report else None,
            "ingested_at":datetime.now(timezone.utc).isoformat(),"page_count":len(pages),
            "transaction_type":structure,"document_type":"8-K with exhibits",
            "ocr_required":any(not p["machine_readable"] for p in pages),
            "warnings":warnings,"pages":pages,"chunks":chunks}
