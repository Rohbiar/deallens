"""Re-run common offline rules without losing an earlier paid model evaluation."""
import copy
import json
import time
from datetime import datetime, timezone
from .ingest import sha256, ingest
from .extract import extract, validate_evidence
from .semantic import identify


def reprocess(root, source_runs=None):
    from .cli import load_latest, new_run_id, derive_bundle, persist
    folder, manifest, bundles = load_latest(root)
    if source_runs:
        from pathlib import Path
        selected=[]; assumptions_bytes=None; parents={}
        for ident, origin in source_runs.items():
            if any(not x or Path(x).name != x for x in (ident, origin)):
                raise ValueError('Invalid source run selection')
            parent=root/'outputs'/origin
            parent_manifest=json.loads((parent/'manifest.json').read_text())
            if parent_manifest['run_id'] != origin or ident not in {d['document_id'] for d in parent_manifest['documents']}:
                raise ValueError('Selected document not in source run')
            raw=(parent/'assumptions.json').read_bytes()
            if assumptions_bytes is not None and json.loads(raw) != json.loads(assumptions_bytes):
                raise ValueError('Cannot consolidate runs with different assumptions')
            assumptions_bytes=raw
            if parents and parent_manifest.get('threshold',.9) != manifest.get('threshold',.9):
                raise ValueError('Cannot consolidate different thresholds')
            if not parents: folder=parent; manifest=parent_manifest
            selected.append({p.stem:json.loads(p.read_text()) for p in (parent/ident).glob('*.json')})
            parents[ident]=origin
        bundles=selected
    if any(b.get('review_events') or any(r.get('review_status')=='verified' for r in b['extractions']) for b in bundles):
        raise ValueError('Offline refresh of human-reviewed runs is not supported; preserve the reviewed run.')
    assumptions=json.loads((folder/'assumptions.json').read_text())
    config_path=root/'config/sources.json'
    sources={s['document_id']:s for s in json.loads(config_path.read_text())} if config_path.exists() else {}
    run_id=new_run_id();revised=[]
    for b in bundles:
        started=time.perf_counter()
        doc=b['document']
        if sha256((root/'data/sources'/doc['file_name']).read_bytes()) != doc['sha256']:
            raise ValueError('Source file changed; refresh requires the original PDF bytes')
        if doc['document_id'] in sources:
            doc=ingest(root/'data/sources'/doc['file_name'], sources[doc['document_id']])
        candidates=copy.deepcopy([r for r in b['extractions'] if r['extraction_method']=='llm'])
        for r in candidates:
            r.setdefault('origin_run_id',r['run_id']);r['run_id']=run_id
            for source in r.get('evidence_sources',[r]):
                if not validate_evidence(source,doc):raise ValueError('Historical proposal evidence is invalid')
        audits=copy.deepcopy(b.get('model_audit',[]))
        for entry in audits:entry.setdefault('origin_run_id',source_runs[b['document']['document_id']] if source_runs else manifest['run_id'])
        from .assessments import annotate
        records=annotate(root,identify(extract(doc,run_id,manifest.get('threshold',.9))+candidates))
        from .provisions import all_evidence
        if any(r.get('evidence') and not all(validate_evidence(s,doc) for s in all_evidence(r)) for r in records):
            raise ValueError('Regenerated evidence or reference context is invalid')
        revised.append(derive_bundle(doc,records,assumptions,elapsed=time.perf_counter()-started,model_audit=audits))
    updated={**manifest,'run_id':run_id,'parent_run_id':manifest['run_id'],
             'mode':'offline_reprocess','started_at':datetime.now(timezone.utc).isoformat(),
             'new_provider_calls':0,'model_results_note':'Historical proposals and audit retained; current prompt was not executed.',
             'offline_code_file_sha256':{str(p.relative_to(root)):sha256(p.read_bytes()) for p in sorted((root/'deallens').glob('*.py'))}}
    if source_runs:
        updated.update(mode='offline_consolidation', source_runs=dict(source_runs),
                       parent_run_ids=sorted(set(source_runs.values())))
        updated.pop('parent_run_id',None)
    updated["assessment_file_sha256"]={str(p.relative_to(root)):sha256(p.read_bytes()) for p in sorted((root/"data/assessments").glob("*.json"))}
    if config_path.exists():updated['source_config_sha256']=sha256(config_path.read_bytes())
    persist(root,updated,revised,assumptions)
    print('Offline refreshed run:',run_id)
    return run_id
