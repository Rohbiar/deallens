"""Selected cross-page completeness regressions, not contract-wide accuracy."""
import json
from pathlib import Path
from deallens.cli import load_latest
from deallens.provisions import all_evidence
from deallens.extract import validate_evidence

FIXTURES = [
    ('bio_techne','rsus','2.03','service-based vesting'),
    ('bio_techne','psus','2.03','maximum performance'),
    ('bio_techne','unvested_options','2.03','target performance'),
    ('bio_techne','fee_triggers_and_tails','7.02','within 12 months'),
    ('bio_techne','extension_dates_and_conditions','7.01','shall automatically extend to June 25, 2027'),
    ('bio_techne','extension_dates_and_conditions','7.01','September 25, 2027'),
    ('organon','rsus','4.3','Pre-2026 Company RSU'),
    ('organon','rsus','4.3','Other Company RSU'),
    ('organon','psus','4.3','target performance'),
    ('organon','extension_dates_and_conditions','9.2','capable of being satisfied at the Closing'),
    ('organon','extension_dates_and_conditions','9.2','irrevocably waived'),
    ('organon','fee_triggers_and_tails','9.5','within nine months'),
    ('uber_delivery_hero','remedy_limitations','4.5','not conditioned on the occurrence of the Offer Completion'),
    ('uber_delivery_hero','fee_triggers_and_tails','13.4','fraudulently or willfully breached'),
    ('uber_delivery_hero','financing_conditions','4.02','requested by BaFin'),
    ('uber_delivery_hero','financing_conditions','4.03','Major Event of Default'),
    ('uber_delivery_hero','financing_conditions','4.04','unless a Major Event of Default'),
    ('uber_delivery_hero','financing_fees_and_stepups','2.09','commencing 120 days after the Effective Date'),
]


def evaluate(root):
    _,manifest,bundles=load_latest(root);by={b['document']['document_id']:b for b in bundles};results=[]
    for ident,field,section,quote in FIXTURES:
        rows=[r for r in by[ident]['extractions'] if r['field_name']==field and r['status']=='source_excerpt']
        matching=[r for r in rows if section in r['candidate_value']['sections'] and quote in ' '.join(s['evidence'] for s in r['evidence_sources'])]
        results.append({'document':ident,'field':field,'section':section,'required_text':quote,'passed':bool(matching)})
    citations=all(validate_evidence(s,b['document']) for b in bundles for r in b['extractions'] if r.get('evidence') for s in all_evidence(r))
    bridge=by['uber_delivery_hero']['analytics']['adaptation']['disclosed_bridge_pricing']
    grid=bridge['pricing_grid'];pricing_pass=(len(grid)==6 and abs(grid[0]['loan_margin_rate']-.0055)<1e-12 and grid[-1]['loan_margin_rate']==.0125 and len(bridge['redacted_components'])==3)
    report={'run_id':manifest['run_id'],'scope':'Agent-curated source passage and qualifier retention fixtures; not independent semantic precision or recall.',
            'passed':sum(r['passed'] for r in results),'total':len(results),'all_context_citations_valid':citations,
            'disclosed_pricing_and_redaction_check':pricing_pass,'results':results}
    (root/'docs/PROVISION_EVALUATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
    for r in results:
        if not r['passed']:print('FAILED',r)
    if not citations or not pricing_pass or report['passed']!=report['total']:raise SystemExit(1)


if __name__=='__main__':evaluate(Path(__file__).resolve().parents[1])
