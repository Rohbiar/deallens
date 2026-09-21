"""Source-faithful sections and explicit cross-reference context.

These records support an extractive answer, not a normalized legal conclusion.
No transaction names, amounts, dates or document-specific section numbers live here.
"""
import re
from .ingest import normalize
from .catalog import FIELDS

VERSION = "source-provisions-1"
LAYERS = ("transaction-agreement", "financing-agreement")


def all_evidence(record):
    """Every attached source, including context, must pass the same byte checks."""
    yield from record.get('evidence_sources', [record])
    for key in ('reference_context','definition_context'):
        for item in record.get(key,[]):
            yield from item.get('sources',[])

# A line-start heading must have whitespace after the section number. A reference
# such as Section 6.01(b), or 'Section 6.01 and ...', is not a heading.
HEADING = re.compile(r"(?m)^\s*(?:Section\s+)?(\d{1,2}\.\d{1,2})\.?\s+([A-Z][^\n]{2,})")
REFERENCE = re.compile(r"\b(?:Sections?|Clauses?)\s+(\d{1,2}\.\d{1,2})(?:\([a-zA-Z0-9]+\))*")
TITLES = {
    "extension_dates_and_conditions": r"Termination|Offer Conditions",
    "offer_or_acceptance_period": r"Offer|Acceptance",
    "cure_periods": r"Termination",
    "regulatory_approvals": r"Regulatory|Reasonable Best Efforts|Further Action|Consents|Offer Conditions|Conditions to",
    "no_injunction_condition": r"Conditions",
    "material_adverse_effect": r"Conditions|Definitions|Defined Terms",
    "remedy_limitations": r"Regulatory|Efforts|Further Action|Appropriate Action|Approvals",
    "fee_triggers_and_tails": r"Fees|Expenses|Termination",
    "superior_or_competing_proposals": r"Solicitation|Acquisition Proposals|Competing|Recommendation",
    "board_recommendation": r"Solicitation|Recommendation",
    "matching_rights": r"Solicitation|Recommendation",
    "termination_rights": r"Termination",
    "funding_sources": r"Financing|Funds",
    "interest_basis": r"Interest",
    "financing_fees_and_stepups": r"Fees|Defined Terms",
    "refinancing_requirements": r"Prepayment|Financing",
    "financing_conditions": r"Conditions.*Borrowing|Certain Funds|Financing",
    "common_shares": r"Conversion of Securities|Conversion of Shares|Effect on Capital",
    "vested_options": r"Equity|Stock Options|Stock-Based|Stock Awards",
    "unvested_options": r"Equity|Stock Options|Stock-Based|Stock Awards",
    "rsus": r"Equity|Restricted Stock|Stock-Based|Stock Awards",
    "psus": r"Equity|Restricted Stock|Stock-Based|Stock Awards",
    "restricted_stock": r"Equity|Restricted Stock|Stock-Based|Stock Awards",
    "employee_stock_purchase_plan": r"Equity|Purchase Plan|Stock-Based|Stock Awards",
    "award_cohort_differences": r"Equity|Stock-Based|Stock Awards",
    "guarantors_or_covered_parties": r"Guarantee|Guaranty|Financing",
}

DEFINITION_TERMS = {
    "interest_basis": ["Applicable Rate", "EURIBOR", "Interest Period"],
    "financing_fees_and_stepups": ["Applicable Rate", "Fee Letter", "Funding Fee", "Duration Fee"],
    "financing_conditions": ["Certain Funds Period", "Major Event of Default", "Major Representations", "Specified Representations", "Availability End Date"],
    "remedy_limitations": ["Substantial Detriment", "Burdensome Condition", "Post-Closing Business", "Delivery Business"],
    "fee_triggers_and_tails": ["Acquisition Proposal", "Competing Proposal", "Superior Proposal", "Company Termination Fee", "Parent Termination Fee"],
}


def slice_sources(sources, start, end):
    """Slice text joined with single spaces back to its original page locators."""
    result=[]; cursor=0
    for source in sources:
        length=len(source['evidence']); a=max(0,start-cursor); b=min(length,end-cursor)
        if b>a:
            s=dict(source);s.update(start=source['start']+a,end=source['start']+b,evidence=source['evidence'][a:b])
            s['locator']=source['locator'].split(':chars')[0]+f":chars{s['start']}-{s['end']}"
            result.append(s)
        cursor+=length+1
    return result


def definitions(sections, layer, terms):
    result=[]
    for term in terms:
        found=[]
        for section in sections:
            if section['layer']!=layer or not re.search(r'Definitions|Defined Terms',section['title'],re.I):continue
            starts=list(re.finditer(r'[“"]([^”"\n]{2,100})[”"]\s+(?:means|has the meaning)',section['text']))
            for i,m in enumerate(starts):
                if m.group(1)!=term:continue
                end=starts[i+1].start() if i+1<len(starts) else len(section['text'])
                found.append(slice_sources(section['sources'],m.start(),end))
        result.append({'term':term,'status':'located' if len(found)==1 else 'missing' if not found else 'ambiguous',
                       'sources':found[0] if len(found)==1 else []})
    return result


def source_span(doc, page, start, end, section):
    return {"document_id": doc["document_id"], "document_sha256": doc["sha256"],
            "document_layer": page["document_layer"], "page": page["page"],
            "start": start, "end": end, "evidence": page["text"][start:end],
            "section": section, "locator": f"{page['locator']}:chars{start}-{end}"}


def section_index(doc):
    """Index whole numbered sections, preserving page boundaries and exact text."""
    result = []
    for layer in LAYERS:
        pages = [p for p in doc["pages"] if p["document_layer"] == layer]
        starts = []
        for i, p in enumerate(pages):
            raw = p.get("raw_text", "")
            matches = list(HEADING.finditer(raw))
            if re.search(r"TABLE OF CONTENTS|^CONTENTS\b", p["text"], re.I):
                continue
            # TOC continuation pages have many headings ending in page numbers.
            if matches and sum(bool(re.search(r"\s{3,}\d+\s*$", m.group(2))) for m in matches) > len(matches)/2:
                continue
            for m in matches:
                line = normalize(m.group())
                offset = p["text"].find(line)
                if offset < 0:
                    continue
                title = normalize(m.group(2)).split(". ", 1)[0]
                if len(title) > 180:  # Untitled numbered clauses retain a short label.
                    title = "Clause " + m.group(1)
                untitled = layer == "transaction-agreement" and not m.group().lstrip().startswith("Section") and not re.match(r"\s*\d+\.\d+\.", m.group())
                starts.append((i, offset, m.group(1), title, untitled))
        for j, (i, start, number, title, untitled) in enumerate(starts):
            end_i, end = starts[j+1][:2] if j+1 < len(starts) else (len(pages)-1, len(pages[-1]["text"]))
            spans = []
            for k in range(i, end_i+1):
                p = pages[k]; a = start if k == i else 0; b = end if k == end_i else len(p["text"])
                if b > a:
                    spans.append(source_span(doc, p, a, b, f"Section {number} {title}"))
            if spans:
                result.append({"number": number, "title": title, "layer": layer,
                               "sources": spans, "text": " ".join(s["evidence"] for s in spans),
                               "untitled": untitled,
                               "boundary": "next_section" if j+1 < len(starts) else "layer_end"})
    return result


def reference_context(sections, selected, max_chars=60000):
    """Resolve explicit section references within the same instrument, one hop.

    Resolving a reference's location is not proof its legal effect is understood.
    The caller retains nested references as unresolved context, never drops them.
    """
    lookup = {}
    for s in sections:
        lookup.setdefault((s["layer"], s["number"]), []).append(s)
    references = []; size = 0
    selected_keys = {(s["layer"], s["number"]) for s in selected}
    seen = set()
    for s in selected:
        for match in REFERENCE.finditer(s["text"]):
            key = (s["layer"], match.group(1))
            if key in seen or key in selected_keys:
                continue
            seen.add(key); targets = lookup.get(key, [])
            entry = {"reference": match.group(), "document_layer": key[0], "section_number": key[1], "sources": []}
            if len(targets) != 1:
                entry["status"] = "missing" if not targets else "ambiguous"
            elif size + len(targets[0]["text"]) > max_chars:
                entry["status"] = "context_limit"
            else:
                t = targets[0]; size += len(t["text"])
                entry.update(status="located", sources=t["sources"],
                             nested_references=sorted(set(m.group() for m in REFERENCE.finditer(t["text"]))))
            references.append(entry)
    return references


def provision_records(doc, run_id, threshold=.9):
    sections = section_index(doc)
    records = []
    for field, title_pattern in TITLES.items():
        pattern = re.compile(FIELDS[field], re.I)
        for layer in LAYERS:
            if layer == "financing-agreement" and field not in {"interest_basis", "financing_fees_and_stepups", "refinancing_requirements", "financing_conditions", "guarantors_or_covered_parties"}:
                continue
            # Lending provisions must use the lending instrument when available.
            if field in {"interest_basis", "financing_fees_and_stepups", "refinancing_requirements", "financing_conditions"}:
                if any(s["layer"] == "financing-agreement" for s in sections) and layer != "financing-agreement":
                    continue
            candidates = []
            for s in sections:
                if s["layer"] != layer or not (pattern.search(s["text"]) or (field=='financing_conditions' and re.search('Certain Funds',s['title']))):
                    continue
                # Number-only takeover clauses have no titles. Match operative
                # text, while requiring a stronger heading match for long sections.
                heading_match = bool(re.search(title_pattern, s["title"], re.I))
                if not heading_match and not s["untitled"]:
                    continue
                if s["boundary"] == "layer_end":
                    continue  # No closing boundary: may include signatures or annexes.
                if re.search(r"Definitions|Defined Terms", s["title"], re.I):
                    continue  # A whole dictionary is not an operative answer.
                if field == "funding_sources" and not re.search(r'committed (?:debt )?financing|funds on hand|Debt Commitment Letter|bridge facility', s['text'], re.I):
                    continue
                candidates.append(s)
            if not candidates:
                continue
            # Never silently truncate a long answer or rank away an exception.
            sources = [x for s in candidates for x in s["sources"]]
            refs = reference_context(sections, candidates)
            terms=DEFINITION_TERMS.get(field,[])
            definition_context=definitions(sections,layer,terms)
            primary = dict(sources[0])
            primary.update(field_name=field, normalized_value=None, currency=None, raw_value=None,
                candidate_value={"kind": "source_provisions", "sections": [s["number"] for s in candidates]},
                evidence_sources=sources, reference_context=refs,
                definition_context=definition_context,
                extraction_method="deterministic", rule_version=VERSION, run_id=run_id,
                confidence=.97, confidence_basis="Exact section extraction; not confidence in legal interpretation",
                status="source_excerpt" if threshold <= .97 else "low_confidence",
                review_status="unreviewed", designation="source_excerpt",
                completeness="not_established",
                limitations=["Verbatim provisions; no complete normalized legal interpretation is asserted.",
                             "Cross-reference lookup is one hop and instrument-local. Defined terms, schedules and nested references may remain unresolved."])
            records.append(primary)
    return records
