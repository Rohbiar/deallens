"""Conservative model-quality warnings; neither semantic proof nor human review."""
import json
import re


def quality_flags(record):
    if record.get('extraction_method')!='llm' or record.get('field_name')!='remedy_limitations':
        return []
    value=record.get('candidate_value')
    text=json.dumps(value,ensure_ascii=False)
    summary=value.get('summary','') if isinstance(value,dict) else ''
    flags=[]
    if re.search(r'no.shop|termination rights|termination fees',summary,re.I) and not re.search(r'divest|substantial detriment|burdensome condition|material adverse|regulatory remed',summary,re.I):
        flags.append({'code':'possible_wrong_field','message':'This remedy summary appears to focus on no-shop or termination provisions. Check that it answers the requested field.'})
    if re.search(r'(?:remedies|remedial actions).{0,70}(?:cannot|must not)|no acceptance of remedies|not accepting remedies|only accepting remedies',text,re.I):
        flags.append({'code':'check_remedy_modality','message':'The candidate uses prohibitive language. Verify whether the source prohibits an action or only limits what a party is required to accept; preserve consent exceptions.'})
    return flags


def flag_candidates(records):
    for record in records:
        if record.get('extraction_method')=='llm':
            record['quality_flags']=quality_flags(record)
    return records
