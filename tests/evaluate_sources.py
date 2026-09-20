"""Evaluate a small disclosed fixture set against the latest complete run."""
import json
from pathlib import Path

def main():
    root=Path(__file__).resolve().parents[1]
    run=json.loads((root/'outputs/latest.json').read_text())['run_id']
    gold=json.loads((root/'tests/source_gold.json').read_text())
    results=[]
    for f in gold['fixtures']:
        records=json.loads((root/'outputs'/run/f['document_id']/'extractions.json').read_text())
        passed=any(r['status']=='supported' and all(r.get('normalized_value' if k=='value' else k)==v for k,v in f.items()) for r in records)
        results.append({'fixture':f,'passed':passed})
    report={'run_id':run,'description':gold['description'],'passed':sum(r['passed'] for r in results),'total':len(results),'results':results}
    (root/'docs/SOURCE_EVALUATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0 if all(r['passed'] for r in results) else 1

if __name__=='__main__':raise SystemExit(main())
