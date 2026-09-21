"""Self-attested local review events. Does not impersonate or authenticate a reviewer."""
import copy
import json
import re
from datetime import datetime, timezone
from .catalog import FIELDS
from .extract import validate_evidence, MONEY, DATE, money, date_iso
from .ingest import sha256
from .semantic import identify, record_id

def packet(manifest, bundles):
    return {"base_run_id":manifest["run_id"],"reviewer":"","human_review_attested":False,
            "instructions":"Review original sources, then add explicit decisions. No decision is pre-approved. Approval/correction covers an entire field and source layer, so inspect all its candidates and cross-references.",
            "decisions":[],"records":[{"document_id":b["document"]["document_id"],"record":r}
                                        for b in bundles for r in b["extractions"] if r.get("evidence") and r.get("status") not in {"superseded","rejected"}]}

def apply_decisions(manifest, bundles, submission, new_run_id):
    if submission.get("base_run_id") != manifest["run_id"]:
        raise ValueError("Stale review packet: base run does not match")
    reviewer=submission.get("reviewer")
    if not isinstance(reviewer,str) or len(reviewer.strip())<2 or submission.get("human_review_attested") is not True:
        raise ValueError("Review requires an identified reviewer and explicit human review attestation")
    decisions=submission.get("decisions")
    if not isinstance(decisions,list) or not decisions:raise ValueError("No explicit decisions provided")
    result=copy.deepcopy(bundles);by_id={b["document"]["document_id"]:b for b in result}
    events=[];groups=set()
    for d in decisions:
        if not isinstance(d,dict):raise ValueError("Invalid review decision")
        document_id=d.get("document_id");field=d.get("field_name");layer=d.get("document_layer")
        group=(document_id,field,layer)
        if document_id not in by_id or field not in FIELDS or layer not in {"8-k-summary","transaction-agreement","financing-agreement"}:
            raise ValueError("Unknown review scope")
        if group in groups:raise ValueError("Multiple decisions for the same field/layer in one packet")
        groups.add(group)
        if d.get("action") not in {"approve","correct","reject"}:raise ValueError("Unknown review action")
        if not isinstance(d.get("reason"),str) or len(d["reason"].strip())<10:raise ValueError("A substantive review reason is required")
        b=by_id[document_id];doc=b["document"];records=b["extractions"]
        index={r["record_id"]:r for r in records};ids=d.get("record_ids")
        if not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)):raise ValueError("Provide distinct evidence record IDs")
        selected=[]
        for rid in ids:
            r=index.get(rid)
            if not r or r["field_name"]!=field or r["document_layer"]!=layer or r.get("status") in {"superseded","rejected"}:
                raise ValueError("Review references an invalid or inactive record")
            if not validate_evidence(r,doc):raise ValueError("Review evidence no longer matches source")
            from .provisions import all_evidence
            for extra in all_evidence(r):
                if not validate_evidence(extra,doc):raise ValueError("Supplemental evidence does not match source")
            selected.append(r)
        now=datetime.now(timezone.utc).isoformat()
        event={"base_run_id":manifest["run_id"],"new_run_id":new_run_id,"reviewer":reviewer.strip(),
               "authentication":"local self-attestation; no identity provider", "reviewed_at":now,
               "document_id":document_id,"document_sha256":doc["sha256"],"decision":copy.deepcopy(d)}
        event["event_id"]=sha256(json.dumps(event,sort_keys=True).encode())[:24]
        if d["action"]=="reject":
            for r in selected:
                r.update(status="rejected",review_status="exception",rejection_reason=d["reason"],review_event_id=event["event_id"])
                if r["normalized_value"] is not None:r["candidate_value"]=r["normalized_value"]
                r["normalized_value"]=None
            events.append(event);continue
        if d.get("complete_field_layer") is not True:
            raise ValueError("Approval/correction requires explicit complete_field_layer attestation")
        if d["action"]=="approve":
            if any(r.get("status")=="source_excerpt" for r in selected):
                raise ValueError("Source excerpts need an explicit normalized interpretation; use correct, not approve")
            values=[r.get("candidate_value",r.get("normalized_value")) for r in selected]
            if any(v is None for v in values) or len({json.dumps(v,sort_keys=True,allow_nan=False) for v in values})!=1:
                raise ValueError("Approve requires one consistent existing value; use correct for a combined interpretation")
            value=values[0];currency=selected[0].get("currency");qualifier=selected[0].get("value_qualifier")
            if any((r.get("currency"),r.get("value_qualifier"))!=(currency,qualifier) for r in selected):
                raise ValueError("Cannot approve mismatched currencies or qualifiers")
        else:
            value=d.get("normalized_value");currency=d.get("currency");qualifier=d.get("value_qualifier")
            if value is None:raise ValueError("A correction requires a non-null value")
        json.dumps(value,allow_nan=False)
        if field in {"consideration_per_share","target_termination_fee","parent_termination_fee","bridge_amount","committed_financing_minimum"}:
            if type(value) not in {int,float} or value<0 or currency not in {"USD","EUR","GBP","JPY","CAD","INR","KRW"} or qualifier not in {"exact","at_least","at_most"}:
                raise ValueError("Reviewed monetary field needs nonnegative number, currency and qualifier")
        if field in {"agreement_date","outside_or_long_stop_date"}:
            from datetime import date
            if not isinstance(value,str):raise ValueError("Reviewed calendar date must be ISO string")
            date.fromisoformat(value)
        if field=="financing_condition" and type(value) is not bool:
            raise ValueError("Financing-condition value must be boolean")
        evidence=[]
        for r in selected:
            evidence.extend(copy.deepcopy(r.get("evidence_sources") or [r]))
        if field in {"consideration_per_share","target_termination_fee","parent_termination_fee","bridge_amount","committed_financing_minimum"}:
            assertions=[]
            for source in evidence:
                text=source["evidence"]
                for match in re.finditer(MONEY,text,re.I):
                    parsed=money(match.group().strip())
                    before=text[max(0,match.start()-30):match.start()]
                    bound="at_least" if re.search(r'at least\s*$|no less than\s*$',before,re.I) else "at_most" if re.search(r'at most\s*$|no more than\s*$',before,re.I) else "exact"
                    if parsed:assertions.append((*parsed,bound))
            if (value,currency,qualifier) not in assertions:
                raise ValueError("Reviewed amount, currency and qualifier must occur together in cited evidence")
        if field in {"agreement_date","outside_or_long_stop_date"}:
            dates={date_iso(m.group()) for source in evidence for m in re.finditer(DATE,source["evidence"])}
            if value not in dates:raise ValueError("Reviewed date is absent from cited evidence")
        fresh=copy.deepcopy(selected[0])
        fresh.update(normalized_value=value,currency=currency,value_qualifier=qualifier,
                     raw_value=d.get("raw_value",selected[0].get("raw_value")),
                     evidence_sources=evidence,status="supported",review_status="verified",
                     designation="fact",extraction_method="hybrid" if any(r["extraction_method"]=="llm" for r in selected) else "manual",
                     reviewer=reviewer.strip(),reviewed_at=now,review_event_id=event["event_id"],
                     review_reason=d["reason"],parent_record_ids=ids,run_id=new_run_id)
        fresh.pop("candidate_value",None);fresh["record_id"]=record_id(fresh)
        for r in records:
            if (r["field_name"],r["document_layer"])==(field,layer) and r.get("status") not in {"superseded","rejected"}:
                r["superseded_by"]=fresh["record_id"]
                if r["normalized_value"] is not None:r["candidate_value"]=r["normalized_value"]
                r.update(normalized_value=None,status="superseded",review_event_id=event["event_id"])
        records.append(fresh);events.append(event)
    for b in result:
        for r in b["extractions"]:r["run_id"]=new_run_id
        b["review_events"]=b.get("review_events",[])+[e for e in events if e["document_id"]==b["document"]["document_id"]]
    return result,events
