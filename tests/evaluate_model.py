"""Selected-fixture retrieval and candidate checks; never human verification.

Run with PYTHONPATH=. python tests/evaluate_model.py. Does not call a provider.
Works on deterministic or live runs and keeps denominators separate.
"""
import json
from collections import Counter
from pathlib import Path
from deallens.cli import load_latest
from deallens.semantic import select_chunks
from deallens.extract import validate_evidence


def evaluate(root):
    _, manifest, bundles = load_latest(root)
    by_id = {b['document']['document_id']: b for b in bundles}
    fixtures = json.loads((root/'tests/source_gold.json').read_text())['fixtures']
    results = []
    for f in fixtures:
        if f['document_id'] not in by_id:
            continue
        b = by_id[f['document_id']]
        chunks = select_chunks(b['document'], f['field_name'], f['document_layer'])
        expected = {('normalized_value' if k == 'value' else k):v for k,v in f.items()}
        baseline = [r for r in b['extractions'] if r['status']=='supported'
                    and all(r.get(k)==v for k,v in expected.items())]
        audits = [a for a in b['model_audit'] if (a['field_name'],a['document_layer']) == (f['field_name'],f['document_layer'])]
        candidates = [r for r in b['extractions'] if r['extraction_method']=='llm'
                      and (r['field_name'],r['document_layer']) == (f['field_name'],f['document_layer'])]
        # Page is checked through every citation, not only the primary citation.
        candidate_matches = [r for r in candidates if r.get('candidate_value')==f['value']
                             and all(r.get(k)==f[k] for k in ('currency','value_qualifier') if k in f)
                             and any(s['page']==f['page'] for s in r.get('evidence_sources',[r]))]
        results.append({'fixture':f, 'baseline_match':bool(baseline),
                        'retrieval_contains_baseline_excerpt':any(r['evidence'] in c['text'] for r in baseline for c in chunks if c['page']==r['page']),
                        'live_request_statuses':[a['status'] for a in audits],
                        'model_candidate_count':len(candidates),
                        'selected_model_value_match':bool(candidate_matches) if audits else None})
    audits = [a for b in bundles for a in b['model_audit']]
    proposed = [r for b in bundles for r in b['extractions'] if r['extraction_method']=='llm']
    evidence = [(b['document'],s) for b in bundles for r in b['extractions'] if r.get('evidence')
                for s in r.get('evidence_sources',[r])]
    usage = Counter()
    for a in audits:
        for key in ('input_tokens','output_tokens','total_tokens'):
            value = (a.get('provider_metadata',{}).get('usage') or {}).get(key)
            if isinstance(value,int): usage[key] += value
    report = {'run_id':manifest['run_id'], 'model':manifest.get('model'),
              'evaluation_kind':'agent-curated selected scalar fixtures; not full semantic accuracy or human review',
              'run_mode':manifest.get('mode'),
              'new_provider_calls':manifest.get('new_provider_calls'),
              'retained_prompt_versions':sorted({a.get('prompt_version','unknown') for a in audits}),
              'response_origin_run_ids':sorted({a.get('origin_run_id',manifest['run_id']) for a in audits}),
              'fixture_count':len(results),
              'retrieved_fixture_excerpts':sum(r['retrieval_contains_baseline_excerpt'] for r in results),
              'model_audit_statuses':dict(Counter(a['status'] for a in audits)),
              'provider_responses':sum(bool(a.get('provider_metadata',{}).get('response_id')) for a in audits),
              'reported_token_usage':dict(usage) or None,
              'model_proposals':len(proposed),
              'nonnull_model_proposals':sum(r.get('candidate_value') is not None for r in proposed),
              'null_model_proposals':sum(r.get('candidate_value') is None for r in proposed),
              'all_evidence_exact':all(validate_evidence(s,d) for d,s in evidence),
              'human_verified_records':sum(b['metrics']['human_verified_records'] for b in bundles),
              'semantic_precision':None,'semantic_recall':None,'dollar_cost':None,
              'limitations':'Retrieval hit means a selected baseline excerpt is in bounded context. Candidate value match does not establish completeness, correct reasoning, or exhaustive citation support. No human gold set; unrequested and budget-exhausted fields are not successful extraction.',
              'results':results}
    (root/'docs/MODEL_EVALUATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))


if __name__=='__main__':
    evaluate(Path(__file__).resolve().parents[1])
