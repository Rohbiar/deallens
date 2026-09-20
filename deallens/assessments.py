"""Disclosed agent annotations, kept separate from review decisions and facts."""
import json


def annotate(root, records):
    by_id={r.get('record_id'):r for r in records}
    for path in sorted((root/'data/assessments').glob('*.json')):
        data=json.loads(path.read_text())
        for note in data['records']:
            record=by_id.get(note['record_id'])
            if record is None:
                continue
            if any(record.get(k)!=note.get(k) for k in ('document_id','document_sha256','field_name')):
                raise ValueError('Agent annotation source identity does not match the record')
            if note.get('human_review') is not False:
                raise ValueError('Agent annotation must not attest human review')
            record['agent_assessment']=note
    return records
