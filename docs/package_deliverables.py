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
    for folder in ['deallens','config','tests','docs','scripts','data/assessments','data/sources',f'outputs/{run}']:
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
    manifest = {'run_id':run,'status':'review candidate; focused v5 evaluated with material errors; v6 citation protocol live validation pending; no expert legal review',
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
