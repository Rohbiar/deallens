"""Re-run common offline rules without losing an earlier paid model evaluation."""
import copy
import json
import time
from datetime import datetime, timezone
from .ingest import sha256
from .extract import extract, validate_evidence
from .semantic import identify


def reprocess(root):
    from .cli import load_latest, new_run_id, derive_bundle, persist
    folder, manifest, bundles = load_latest(root)
    if any(b.get('review_events') or any(r.get('review_status')=='verified' for r in b['extractions']) for b in bundles):
        raise ValueError('Offline refresh of human-reviewed runs is not supported; preserve the reviewed run.')
    assumptions=json.loads((folder/'assumptions.json').read_text())
    run_id=new_run_id();revised=[]
    for b in bundles:
        started=time.perf_counter()
        doc=b['document']
        if sha256((root/'data/sources'/doc['file_name']).read_bytes()) != doc['sha256']:
            raise ValueError('Source file changed; refresh requires the original PDF bytes')
        candidates=copy.deepcopy([r for r in b['extractions'] if r['extraction_method']=='llm'])
        for r in candidates:
            r.setdefault('origin_run_id',r['run_id']);r['run_id']=run_id
            for source in r.get('evidence_sources',[r]):
                if not validate_evidence(source,doc):raise ValueError('Historical proposal evidence is invalid')
        audits=copy.deepcopy(b.get('model_audit',[]))
        for entry in audits:entry.setdefault('origin_run_id',manifest['run_id'])
        from .assessments import annotate
        records=annotate(root,identify(extract(doc,run_id,manifest.get('threshold',.9))+candidates))
        revised.append(derive_bundle(doc,records,assumptions,elapsed=time.perf_counter()-started,model_audit=audits))
    updated={**manifest,'run_id':run_id,'parent_run_id':manifest['run_id'],
             'mode':'offline_reprocess','started_at':datetime.now(timezone.utc).isoformat(),
             'new_provider_calls':0,'model_results_note':'Historical proposals and audit retained; current prompt was not executed.',
             'offline_code_file_sha256':{str(p.relative_to(root)):sha256(p.read_bytes()) for p in sorted((root/'deallens').glob('*.py'))}}
    updated["assessment_file_sha256"]={str(p.relative_to(root)):sha256(p.read_bytes()) for p in sorted((root/"data/assessments").glob("*.json"))}
    persist(root,updated,revised,assumptions)
    print('Offline refreshed run:',run_id)
    return run_id
