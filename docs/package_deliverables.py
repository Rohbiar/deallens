"""Build a review archive with explicit inputs, hashes and genuine Git history.

Run from any directory with Python 3.11+. No credentials or virtual environments
are included. Existing immutable run folders are preserved in the working repo;
the archive carries the latest run plus the complete SQLite history.
"""
import hashlib
import json
import sqlite3
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    run = json.loads((ROOT/'outputs/latest.json').read_text())['run_id']
    if Path(run).name != run:
        raise ValueError('Invalid run ID')
    for name in ['REQUIREMENTS_AUDIT.json','SOURCE_EVALUATION.json','PROVISION_EVALUATION.json','MODEL_EVALUATION.json']:
        if json.loads((ROOT/'docs'/name).read_text()).get('run_id')!=run:
            raise ValueError('Regenerate stale validation report: '+name)
    semantic=json.loads((ROOT/'docs/SEMANTIC_EVALUATION.json').read_text())
    predictions=json.loads((ROOT/'docs/SEMANTIC_PREDICTIONS.json').read_text())
    semantic_metrics=semantic.get('metrics',{})
    if semantic_metrics.get('bounded_supported_assertion_denominator') != 72:
        raise ValueError('Semantic evaluation does not match the frozen reference denominator')
    if semantic_metrics.get('unresolved_reference_case_denominator') != 4:
        raise ValueError('Semantic evaluation does not cover all unresolved reference cases')
    if predictions.get('schema_version') != '1.0' or len(predictions.get('cases',[])) != 16:
        raise ValueError('Regenerate semantic predictions for the frozen reference set')
    if len({case.get('case_id') for case in predictions['cases']}) != 16:
        raise ValueError('Semantic predictions contain missing or duplicate cases')
    requirements=json.loads((ROOT/'docs/REQUIREMENTS_AUDIT.json').read_text())
    if requirements.get('bounded_semantic_evaluation') != semantic_metrics:
        raise ValueError('Requirement audit and semantic evaluation disagree')
    if run not in (ROOT/'docs/SUBMISSION_STATUS.md').read_text():
        raise ValueError('Regenerate submission status for the packaged run')
    run_manifest=json.loads((ROOT/'outputs'/run/'manifest.json').read_text())
    for item in run_manifest['documents']:
        document_root=ROOT/'outputs'/run/item['document_id']
        terms=json.loads((document_root/'structured_terms.json').read_text())
        if not terms or not all(t.get('schema_version')=='structured-terms/v1' for t in terms):
            raise ValueError('Missing or invalid structured terms: '+item['document_id'])
        for name in ('structured_comparisons.json','structured_timeline.json','structured_exceptions.json'):
            if not (document_root/name).exists():
                raise ValueError('Missing structured artifact: '+item['document_id']+'/'+name)
    dest = ROOT/'outputs/deliverables'
    dest.mkdir(exist_ok=True)
    archive = dest/'DealLens_review_package.zip'
    bundle = dest/'history.bundle'
    subprocess.run(['git','bundle','create',str(bundle),'--all'],cwd=ROOT,check=True)
    # SQLite backup gives a consistent snapshot, including any committed WAL.
    with sqlite3.connect(ROOT/'outputs/deallens.sqlite') as source:
        with sqlite3.connect(dest/'deallens.sqlite') as target:
            source.backup(target)
    # Carry the persistent reservation ledger so restoring the package cannot
    # accidentally reset the authorized API allowance.
    budget_snapshot = None
    if (ROOT/'outputs/api_budget.sqlite').exists():
        budget_snapshot = dest/'api_budget.sqlite'
        with sqlite3.connect(ROOT/'outputs/api_budget.sqlite') as source:
            with sqlite3.connect(budget_snapshot) as target:
                source.backup(target)
    files = [p for p in ROOT.iterdir() if p.is_file() and p.name in
             {'README.md','EXECUTION_PLAN.md','AGENT_WORKFLOW.md','requirements.txt','requirements-tested.txt','pyproject.toml','.gitignore'}]
    lineage=sorted(set(run_manifest.get('parent_run_ids',[])) |
                   set(run_manifest.get('source_runs',{}).values()) |
                   ({run_manifest['parent_run_id']} if run_manifest.get('parent_run_id') else set()))
    for ancestor in lineage:
        if Path(ancestor).name != ancestor: raise ValueError('Invalid lineage run')
    for folder in ['deallens','config','tests','docs','scripts','data/assessments','data/sources',f'outputs/{run}'] + [f'outputs/{ancestor}' for ancestor in lineage]:
        files += [p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    files += [ROOT/'outputs/latest.json']
    # Only include a packet tied to the packaged run; never reuse stale decisions.
    packet_paths = []
    for p in (ROOT/'outputs').glob('review_packet*.json'):
        packet = json.loads(p.read_text())
        if packet.get('base_run_id') == run:
            packet_paths.append(p)
    files += packet_paths
    content = {str(p.relative_to(ROOT)):p.read_bytes() for p in files}
    if budget_snapshot:
        content['outputs/api_budget.sqlite'] = budget_snapshot.read_bytes()
    content['history.bundle'] = bundle.read_bytes()
    content['outputs/deallens.sqlite'] = (dest/'deallens.sqlite').read_bytes()
    content['RESTORE_HISTORY.txt'] = b'To restore the genuine repository history: git clone history.bundle deallens-history\nThe package contains latest run JSON plus SQLite history; older run JSON remains in the working repository.\n'
    manifest = {'run_id':run,'status':'submission candidate with disclosed limitations; structured interpretations remain unreviewed candidates; bounded semantic recall is zero; no human verification',
                'working_tree_changes':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).splitlines(),
                'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                'files':{name:hashlib.sha256(data).hexdigest() for name,data in sorted(content.items())}}
    content['PACKAGE_MANIFEST.json'] = (json.dumps(manifest,indent=2)+'\n').encode()
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in sorted(content.items()): z.writestr('DealLens/'+name,data)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for name,digest in manifest['files'].items():
            assert hashlib.sha256(z.read('DealLens/'+name)).hexdigest()==digest
    (dest/'SHA256SUMS.txt').write_text(hashlib.sha256(archive.read_bytes()).hexdigest()+'  '+archive.name+'\n')
    print(archive)
    print(f'{len(content)} files; {archive.stat().st_size:,} bytes; hashes verified')


if __name__=='__main__':
    build()
