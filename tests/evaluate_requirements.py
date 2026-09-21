"""Assignment artifact and coverage audit. Completeness is not inferred from files."""
import json
from pathlib import Path
from deallens.cli import load_latest
from deallens.catalog import FIELDS, QUESTIONS
from deallens.extract import validate_evidence
from deallens.ingest import sha256
from deallens.qa import answer, UNSUPPORTED
from deallens.provisions import all_evidence


def evaluate(root):
    folder,manifest,bundles=load_latest(root)
    cases=[]
    for b in bundles:
        doc=b['document'];records=b['extractions']
        checks={
            'original_pdf_hash_matches':sha256((root/'data/sources'/doc['file_name']).read_bytes())==doc['sha256'],
            'every_catalog_field_has_explicit_result':set(FIELDS)=={r['field_name'] for r in records},
            'every_field_has_comparison':set(FIELDS)=={c['field_name'] for c in b['comparisons']},
            'all_twelve_question_categories':set(QUESTIONS)==set(b['qa']),
            'every_retained_citation_matches_source':all(validate_evidence(s,doc) for r in records if r.get('evidence') for s in all_evidence(r)),
            'model_candidates_never_promoted':all(r['normalized_value'] is None and r['review_status']!='verified' for r in records if r['extraction_method']=='llm'),
            'strict_qa_abstains_without_human_approval':all(answer(q,records,b['comparisons'],True)['answer']==UNSUPPORTED for q in QUESTIONS) if not b['metrics']['human_verified_records'] else None,
        }
        fields=[]
        for name in FIELDS:
            rs=[r for r in records if r['field_name']==name]
            supported=[r for r in rs if r['status']=='supported']
            fields.append({'field_name':name,'has_machine_supported_value':bool(supported),
                'has_source_section_excerpt':any(r['status']=='source_excerpt' for r in rs),
                'comparison':next(c['classification'] for c in b['comparisons'] if c['field_name']==name),
                'layers':{layer:sorted({r['status'] for r in rs if r['document_layer']==layer}) for layer in ['8-k-summary','transaction-agreement','financing-agreement']},
                'source_pages':sorted({r['page'] for r in rs if r.get('evidence')}),
                'complete_legal_interpretation_verified':False})
        cases.append({'document_id':doc['document_id'],'checks':checks,'machine_supported_fields':b['metrics']['machine_supported_fields'],
                      'source_excerpt_fields':b['metrics'].get('source_excerpt_fields',0),
                      'filing_date_status':doc.get('filing_date_status'),
                      'qa_statuses':{q:a['status'] for q,a in b['qa'].items()},'field_coverage':fields,
                      'scenarios':sorted({r['scenario_id'] for r in b['analytics']['rows']}),
                      'strategies':sorted({r['strategy'] for r in b['analytics']['rows']}),
                      'blocked_scenarios':b['analytics'].get('blocked_scenarios',[])})
    bio=next(c for c in cases if c['document_id']=='bio_techne')
    required={'rates_up_25','rates_down_25','rates_up_50','rates_up_25_credit_wider_20','first_extension','final_extension','failure_rates_down_25'}
    report={'run_id':manifest['run_id'],'audit_type':'machine artifact/control checks plus disclosed coverage; not expert approval',
            'all_machine_checks_pass':all(v is not False for c in cases for v in c['checks'].values()),
            'all_required_bio_scenarios_present':required.issubset(bio['scenarios']),
            'complete_semantic_extraction':False,'expert_legal_review_performed':False,
            'remaining_requirements':['Complete normalized complex extraction and direct QA coverage; source sections are not semantic completion','Broader semantic evaluation beyond selected fixtures','Bio-Techne filing-index date verification (PDF metadata reported); omitted schedules and redacted terms unavailable','Independent semantic gold set; precision and recall','Candidate technical ownership and final submission decision'],
            'documents':cases}
    (root/'docs/REQUIREMENTS_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='documents'},indent=2))
    if not report['all_machine_checks_pass'] or not report['all_required_bio_scenarios_present']:raise SystemExit(1)

if __name__=='__main__':evaluate(Path(__file__).resolve().parents[1])
