"""Assignment artifact and coverage audit. Completeness is not inferred from files."""
import json
from pathlib import Path
from deallens.cli import load_latest
from deallens.catalog import FIELDS, QUESTIONS
from deallens.extract import validate_evidence
from deallens.ingest import sha256
from deallens.qa import answer, UNSUPPORTED
from deallens.provisions import all_evidence
from deallens.term_validation import validate_term


def evaluate(root):
    folder,manifest,bundles=load_latest(root)
    cases=[]
    for b in bundles:
        doc=b['document'];records=b['extractions']
        terms=b.get('structured_terms',[])
        contexts={(r.get('field_name'),r.get('document_layer')):r.get('context_bundle')
                  for r in records if r.get('context_bundle')}
        term_validation=[]
        for term in terms:
            context=contexts.get((term.get('field_name'),term.get('document_layer')))
            term_validation.append(bool(context) and validate_term(term,context)['valid'])
        checks={
            'original_pdf_hash_matches':sha256((root/'data/sources'/doc['file_name']).read_bytes())==doc['sha256'],
            'every_catalog_field_has_explicit_result':set(FIELDS)=={r['field_name'] for r in records},
            'every_field_has_comparison':set(FIELDS)=={c['field_name'] for c in b['comparisons']},
            'all_twelve_question_categories':set(QUESTIONS)==set(b['qa']),
            'every_retained_citation_matches_source':all(validate_evidence(s,doc) for r in records if r.get('evidence') for s in all_evidence(r)),
            'model_candidates_never_promoted':all(r['normalized_value'] is None and r['review_status']!='verified' for r in records if r['extraction_method']=='llm'),
            'strict_qa_abstains_without_human_approval':all(
                answer(q,records,b['comparisons'],True,structured_terms=terms)['answer']==UNSUPPORTED
                for q in QUESTIONS) if not b['metrics']['human_verified_records'] else None,
            'structured_artifacts_present':all(key in b for key in ('structured_terms','structured_comparisons','structured_timeline')),
            'structured_terms_schema_and_provenance_valid':bool(terms) and all(term_validation),
            'structured_candidates_not_human_verified':all(
                term.get('review_status')!='verified' for term in terms
                if term.get('status') in {'candidate','unresolved'}),
            'structured_timeline_never_asserts_occurrence':all(
                event.get('occurrence_status')=='not_established'
                for event in b.get('structured_timeline',[])),
            'structured_qa_components_exposed':all(
                'supported_components' in row and 'unresolved_components' in row
                for row in b.get('qa',{}).values()),
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
    required={'rates_up_25','rates_down_25','rates_up_50','rates_up_25_credit_wider_20','first_extension','final_extension','failure'}
    semantic_path=root/'docs/SEMANTIC_EVALUATION.json'
    semantic=json.loads(semantic_path.read_text()) if semantic_path.exists() else None
    report={'run_id':manifest['run_id'],'audit_type':'machine artifact/control checks plus disclosed coverage; not expert approval',
            'all_artifact_integrity_checks_pass':all(v is not False for c in cases for v in c['checks'].values()),
            'all_required_bio_scenarios_present':required.issubset(bio['scenarios']),
            'required_bio_scenarios':sorted(required),
            'bounded_semantic_evaluation':semantic.get('metrics') if semantic else None,
            'complete_semantic_extraction':False,'expert_legal_review_performed':False,
            'remaining_requirements':['Candidate structured interpretations remain unverified and do not complete direct QA coverage','Broader or human semantic evaluation beyond the bounded agent-curated reference set','Bio-Techne filing-index date verification (PDF metadata reported); omitted schedules and redacted terms unavailable','Contract-wide precision and recall remain unmeasured','Candidate technical ownership and final submission decision'],
            'documents':cases}
    (root/'docs/REQUIREMENTS_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='documents'},indent=2))
    if not report['all_artifact_integrity_checks_pass'] or not report['all_required_bio_scenarios_present']:raise SystemExit(1)

if __name__=='__main__':evaluate(Path(__file__).resolve().parents[1])
