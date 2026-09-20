"""Deterministic scalar extraction and conservative clause retrieval.

Complex legal provisions are candidates, never approved interpretations. Model
outputs enter the same evidence validation and comparison gates (see model.py).
"""
from __future__ import annotations
import re
from datetime import datetime
from .catalog import FIELDS
from .ingest import normalize

DATE = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
MONEY = r'(?:\$|€|EUR\s*|USD\s*)(\d[\d,]*(?:\.\d+)?)\s*(million|billion)?'
SCALARS = {"consideration_per_share", "agreement_date", "outside_or_long_stop_date", "bridge_amount",
           "target", "parent_or_bidder", "acquisition_vehicle", "transaction_type", "consideration_type", "financing_condition", "financing_maturity",
           "target_termination_fee", "parent_termination_fee", "approval_or_tender_threshold", "committed_financing_minimum"}

def date_iso(raw):
    for fmt in ("%B %d, %Y", "%B %d %Y", "%d %B %Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass
    return None

def money(raw):
    m = re.fullmatch(MONEY, raw.strip(), re.I)
    if not m:
        return None
    multiplier = {None:1,"million":1e6,"billion":1e9}[m.group(2).lower() if m.group(2) else None]
    return float(m.group(1).replace(",", ""))*multiplier, "EUR" if re.match(r'€|EUR',raw) else "USD"

def section_at(text, position):
    headings = list(re.finditer(r'(?:Section\s+\d+\.\d+\s+[A-Z][A-Za-z ,;–-]{3,85}|\b\d+\.\d+\s+[A-Z][A-Za-z ,;–-]{3,65})', text[:position+1]))
    return headings[-1].group().strip() if headings else "Page text (section unresolved)"

def evidence_record(doc, page, field, start, end, run_id, value=None, currency=None, raw_value=None):
    qualifier="exact"
    if currency and raw_value:
        pos=page["text"].find(raw_value,start,end)
        if pos>=0:
            before=page["text"][max(0,pos-30):pos]
            if re.search(r'at least\s*$|no less than\s*$',before,re.I):qualifier="at_least"
            elif re.search(r'at most\s*$|no more than\s*$',before,re.I):qualifier="at_most"
            start=max(0,min(start,pos-35))
    return {"field_name":field,"normalized_value":value,"currency":currency,
            "value_qualifier":qualifier if currency else None,
            "raw_value":raw_value,"document_id":doc["document_id"],
            "document_sha256":doc["sha256"],"document_layer":page["document_layer"],
            "page":page["page"],"section":section_at(page["text"], start),
            "locator":f"{page['locator']}:chars{start}-{end}","start":start,"end":end,
            "evidence":page["text"][start:end],"extraction_method":"deterministic",
            "confidence":0.97 if value is not None else 0.55,
            "confidence_basis":"rule score, not a calibrated probability",
            "review_status":"unreviewed" if value is not None else "exception",
            "status":"supported" if value is not None else "requires_review",
            "designation":"fact" if value is not None else "candidate_evidence",
            "run_id":run_id,"rule_version":"rules-1.0"}

def scalar_matches(field, text):
    """Yield exact evidence spans and values; never use document identity."""
    if field in {"target", "parent_or_bidder", "acquisition_vehicle"}:
        from .parties import party_declarations
        for matched_field,start,end,name,alias in party_declarations(text):
            if field == matched_field:
                yield start,end,name,None,name
    elif field == "consideration_per_share":
        patterns = [r'(?:right to receive|cash consideration per.{0,65}?of|Offer Price shall (?:be|amount to))\s*('+MONEY+r')',
                    r'[“\"](?:Per Share )?Merger Consideration[”\"]\s+means\s*('+MONEY+r')',
                    r'('+MONEY+r')\s+(?:in cash|per.{0,35}Share).{0,90}?(?:Merger Consideration|Offer Price)',
                    r'(?:Offer Price|offer price).{0,35}?('+MONEY+r')\s+per']
        for pattern in patterns:
            for m in re.finditer(pattern,text,re.I):
                amounts = list(re.finditer(MONEY,m.group(),re.I))
                if len(amounts)==1:
                    raw=amounts[0].group().strip(); parsed=money(raw)
                    if parsed and parsed[0]>0:
                        yield m.start(),m.end(),parsed[0],parsed[1],raw
    elif field == "agreement_date":
        pattern = r'(?:(?:AGREEMENT AND PLAN OF MERGER|BUSINESS COMBINATION AGREEMENT).{0,55}?dated as of\s*|On\s*)('+DATE+r')'
        for m in re.finditer(pattern,text,re.I):
            if m.group().lower().startswith("on") and not re.search(r'entered into',text[m.end():m.end()+300],re.I):
                continue
            value=date_iso(m.group(1))
            if value: yield m.start(),min(len(text),m.end()+250),value,None,m.group(1)
    elif field == "outside_or_long_stop_date":
        pattern = '('+DATE+r')\s*\((?:(?:as may be extended[^)]{0,100}?)?the\s+[“\"]?)(?:Outside Date|Long[- ]Stop Date)[”\"]?'
        for m in re.finditer(pattern,text,re.I):
            value=date_iso(m.group(1))
            if value: yield max(0,m.start()-100),min(len(text),m.end()+180),value,None,m.group(1)
    elif field == "bridge_amount":
        pattern = r'(?:bridge loan commitments.{0,80}?amount of|aggregate amount of commitments.{0,30})\s*('+MONEY+r')'
        for m in re.finditer(pattern,text,re.I):
            raw=re.search(MONEY,m.group(),re.I).group().strip(); parsed=money(raw)
            if parsed: yield m.start(),m.end(),parsed[0],parsed[1],raw
    elif field == "committed_financing_minimum":
        for m in re.finditer(r'committed financing.{0,200}?amounting to no less than\s*('+MONEY+r')',text,re.I):
            raw=re.search(MONEY,m.group(),re.I).group().strip();parsed=money(raw)
            if parsed:yield m.start(),m.end(),parsed[0],parsed[1],raw
    elif field == "transaction_type":
        for pattern,value in [(r'voluntary public takeover offer','public_takeover_offer'),
                              (r'(?:Merger Sub|merger subsidiary).{0,100}(?:will|shall) (?:be )?merge[d]? with and into','merger')]:
            for m in re.finditer(pattern,text,re.I):yield m.start(),m.end(),value,None,m.group()
    elif field == "consideration_type":
        for m in re.finditer(r'cash consideration per.{0,60}Share|right to receive\s*'+MONEY+r'\s+in cash',text,re.I):
            yield m.start(),m.end(),'cash',None,m.group()
    elif field == "financing_condition":
        patterns=[r'not a condition to the Closing.{0,250}obtain financing',
                  r'obligations hereunder are not subject to any conditions.{0,180}obtain financing']
        for pattern in patterns:
            for m in re.finditer(pattern,text,re.I):yield m.start(),min(len(text),m.end()+90),False,None,m.group()
    elif field == "financing_maturity":
        pattern=r'(?:mature on the date that is|Maturity Date[”\"]? means.{0,70}?)\s*(\d+) days after the (Closing Date)'
        for m in re.finditer(pattern,text,re.I):
            yield m.start(),m.end(),{"offset":int(m.group(1)),"unit":"calendar_days","anchor":m.group(2)},None,m.group()
    elif field in {"target_termination_fee","parent_termination_fee"}:
        role = 'Company' if field=='target_termination_fee' else '(?:Parent|Bidder)'
        label = 'Company Termination Fee' if field=='target_termination_fee' else 'Parent Termination Fee'
        patterns=[rf'{role}\s+(?:will be |is )?required to pay.{{0,85}}?termination fee (?:equal to|of)\s*('+MONEY+r')',
                  '('+MONEY+rf')\s*\(the [“\"]{label}[”\"]\)',
                  rf'[“\"]{label}[”\"]\s+means.{{0,35}}?('+MONEY+r')',
                  rf'{label}\s+shall amount to\s*('+MONEY+r')']
        if field=='parent_termination_fee':patterns.append(r'Regulatory Reverse Fee shall amount to\s*('+MONEY+r')')
        for pattern in patterns:
            for m in re.finditer(pattern,text,re.I):
                amounts=list(re.finditer(MONEY,m.group(),re.I))
                if len(amounts)==1:
                    raw=amounts[0].group().strip();parsed=money(raw)
                    if parsed:yield m.start(),m.end(),parsed[0],parsed[1],raw
    elif field == 'approval_or_tender_threshold':
        # Preserve the denominator in exact source language; do not equate voting power with share count.
        patterns=[r'majority of the voting power of all of the Shares outstanding and entitled to vote',
                  r'majority of the outstanding Shares entitled to vote',
                  r'at least 50% of the number of.{0,220}?plus one share, excluding treasury shares']
        for pattern in patterns:
            for m in re.finditer(pattern,text,re.I):yield m.start(),m.end(),m.group(),None,m.group()

def extract(doc, run_id, threshold=0.9):
    if not 0 <= threshold <= 1: raise ValueError("Invalid confidence threshold")
    records=[]
    for field,pattern in FIELDS.items():
        for layer in ("8-k-summary","transaction-agreement","financing-agreement"):
            candidates=[]; scalar=[]
            for page in doc["pages"]:
                if page["document_layer"]!=layer or not page["machine_readable"]: continue
                text=page["text"]
                # Index pages are not operative provisions.
                if re.search(r'TABLE OF CONTENTS|^CONTENTS\b',text,re.I): continue
                if field in SCALARS and (field not in {"target", "parent_or_bidder", "acquisition_vehicle"} or layer=="transaction-agreement"):
                    for start,end,value,currency,raw in scalar_matches(field,text):
                        scalar.append(evidence_record(doc,page,field,start,end,run_id,value,currency,raw))
                for match in re.finditer(pattern,text,re.I):
                    start=max(0,match.start()-200);end=min(len(text),match.end()+1000)
                    record=evidence_record(doc,page,field,start,end,run_id)
                    # Prefer substantive paragraphs over bare references and definitions.
                    score=len(re.findall(r'will|shall|provided|subject|means|terminated|converted',record["evidence"],re.I))
                    candidates.append((score,record))
            unique={}
            for r in scalar:
                unique.setdefault((str(r["normalized_value"]),r["currency"],r.get("value_qualifier")),[]).append(r)
            if len(unique)>1:
                for r in scalar:
                    r["candidate_value"]=r["normalized_value"];r["normalized_value"]=None
                    r.update(status="conflict",review_status="exception",designation="candidate_evidence")
            elif threshold>0.97:
                for r in scalar:
                    r["candidate_value"]=r["normalized_value"];r["normalized_value"]=None
                    r.update(status="low_confidence",review_status="exception",designation="candidate_evidence")
            records.extend(scalar)
            if not scalar:
                used=[]
                for score,r in sorted(candidates,key=lambda x:(-x[0],x[1]["page"],x[1]["start"])):
                    if any(p==r["page"] and abs(s-r["start"])<600 for p,s in used): continue
                    used.append((r["page"],r["start"]));records.append(r)
                    if len(used)>=6:break
                if not used:
                    records.append({"field_name":field,"normalized_value":None,"currency":None,"raw_value":None,
                                    "document_id":doc["document_id"],"document_layer":layer,"page":None,
                                    "section":None,"evidence":None,"extraction_method":"deterministic",
                                    "confidence":0,"review_status":"exception","status":"not_found",
                                    "designation":"candidate_evidence","run_id":run_id})
    return records

def validate_evidence(record, doc):
    if record.get("document_id") != doc["document_id"]: return False
    if record.get("document_sha256") != doc["sha256"]: return False
    p=record.get("page")
    if not isinstance(p,int) or not 1<=p<=len(doc["pages"]): return False
    page=doc["pages"][p-1]
    if record.get("document_layer")!=page["document_layer"]: return False
    start,end=record.get("start"),record.get("end")
    if not isinstance(start,int) or not isinstance(end,int) or not 0<=start<end<=len(page["text"]): return False
    return bool(record.get("evidence")) and page["text"][start:end]==record["evidence"]

def comparison(records):
    records=[r for r in records if r.get("status") not in {"superseded","rejected"}]
    output=[]
    for field in FIELDS:
        sides={layer:[r for r in records if r["field_name"]==field and r["document_layer"]==layer]
               for layer in ("8-k-summary","transaction-agreement")}
        # Financing exhibit is the relevant underlying contract for financing fields.
        if field in {"bridge_amount","financing_maturity","interest_basis","financing_fees_and_stepups","financing_conditions","refinancing_requirements"}:
            financing=[r for r in records if r["field_name"]==field and r["document_layer"]=="financing-agreement" and r.get("evidence")]
            if financing:sides["transaction-agreement"]=financing
        a,b=sides.values()
        av=[r for r in a if r["status"]=="supported"];bv=[r for r in b if r["status"]=="supported"]
        import json
        def values(items):
            return {(json.dumps(r["normalized_value"],sort_keys=True),r["currency"],r.get("value_qualifier")) for r in items}
        if any(r["status"]=="conflict" for r in a+b) or len(values(av))>1 or len(values(bv))>1:status="conflict"
        elif av and bv:
            x=values(av);y=values(bv)
            if x!=y:status="conflict"
            elif {r["raw_value"] or r.get("evidence") for r in av}=={r["raw_value"] or r.get("evidence") for r in bv}:status="match"
            else:status="normalized match"
        elif av and not any(r.get("evidence") for r in b):status="summary only"
        elif bv and not any(r.get("evidence") for r in a):status="agreement only"
        else:status="unresolved"
        output.append({"field_name":field,"classification":status,"summary":a,"agreement":b,
                       "comparison_note":"Different amounts, currencies or exact/minimum/maximum qualifiers require review; a flagged difference is not itself a legal conclusion of contradiction.",
                       "source_hierarchy":"Relevant executed agreement > filing summary > other exhibit; any detected conflict blocks canonical value.",
                       "canonical_value":None if status in {"conflict","unresolved"} else (bv or av)[0]["normalized_value"]})
    return output

def timeline(doc,records):
    fields={"agreement_date","outside_or_long_stop_date","extension_dates_and_conditions","offer_or_acceptance_period",
            "cure_periods","expected_closing_timing","approval_or_tender_threshold","regulatory_approvals","financing_maturity","financing_fees_and_stepups"}
    events=[];seen=set()
    for r in records:
        if r.get("status") in {"superseded","rejected"}:continue
        if r["field_name"] not in fields or not r.get("evidence"):continue
        text=r["evidence"]
        if r["field_name"]=="expected_closing_timing":kind="non_binding_estimate"
        elif re.search(r'automatic(?:ally)? extend',text,re.I):kind="automatic_conditional_extension"
        elif re.search(r'elect to extend|may.{0,100}extend|authorized by BaFin',text,re.I):kind="party_or_regulator_election"
        elif re.search(r'\bdays?\b.{0,40}(?:after|following)|(?:within|prior to).{0,30}\bdays?\b',text,re.I):kind="relative"
        elif re.search(r'if|provided|subject to',text,re.I):kind="conditional"
        else:kind="fixed_date" if r["status"]=="supported" else "unresolved"
        dates=[{"raw":m.group(),"iso":date_iso(m.group())} for m in re.finditer(DATE,text)]
        key=(r["field_name"],r["page"],r.get("start"))
        if key in seen:continue
        seen.add(key)
        events.append({"event":r["field_name"],"date_type":kind,"candidate_dates":dates,
                       "resolved_date":r["normalized_value"] if r["status"]=="supported" and r["field_name"] in {"agreement_date","outside_or_long_stop_date"} else None,
                       "status":r["status"],"note":"Dates in supporting text are candidates; do not schedule from them without resolving conditions and cross-references.","source":r})
    return events
