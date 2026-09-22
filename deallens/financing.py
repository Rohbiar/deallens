"""Disclosed bridge pricing, separated from assumed draw and market levels."""
import math
import re
from .provisions import section_index, definitions


def pricing_scenario_inputs(disclosure, *, pricing_level=None,
                            assumed_draw=None, benchmark_rate=None):
    """Keep disclosed bridge terms separate from selected synthetic inputs.

    The public pricing grid is a fact. Rating selection, utilization and the
    benchmark are scenario/market assumptions. Redacted components remain
    explicitly unavailable and are never populated from a synthetic proxy.
    """
    redacted = disclosure.get('redacted_components', [])
    result = {
        'schema_version': 'bridge-scenario-inputs/v1',
        'contractual_facts': {
            'status': disclosure.get('status'),
            'benchmarks': list(disclosure.get('benchmarks', [])),
            'pricing_grid': list(disclosure.get('pricing_grid', [])),
            'sources': list(disclosure.get('sources', [])),
            'designation': 'fact',
        },
        'market_inputs': {
            'benchmark_rate': benchmark_rate,
            'designation': 'assumption',
        },
        'scenario_assumptions': {
            'pricing_level': pricing_level,
            'assumed_draw': assumed_draw,
            'designation': 'assumption',
        },
        'unavailable_contract_terms': {
            name: {'value': None, 'designation': 'fact', 'status': 'redacted'}
            for name in redacted
        },
        'calculation': None,
        'blocked_reasons': [],
    }
    if disclosure.get('status') != 'disclosed_grid':
        result['blocked_reasons'].append('Disclosed pricing grid is unavailable or unresolved.')
        return result
    selected = [row for row in disclosure.get('pricing_grid', [])
                if row.get('pricing_level') == pricing_level]
    if len(selected) != 1:
        result['blocked_reasons'].append('A unique disclosed pricing level must be selected as a scenario assumption.')
    if (type(assumed_draw) not in {int, float} or
            not math.isfinite(assumed_draw) or assumed_draw < 0):
        result['blocked_reasons'].append('A non-negative assumed draw is required.')
    if (type(benchmark_rate) not in {int, float} or
            not math.isfinite(benchmark_rate)):
        result['blocked_reasons'].append('A numeric market benchmark assumption is required.')
    if result['blocked_reasons']:
        return result
    row = selected[0]
    result['calculation'] = {
        'pricing_level': pricing_level,
        'loan_margin_rate': row['loan_margin_rate'],
        'annualized_interest': assumed_draw * (benchmark_rate + row['loan_margin_rate']),
        'designation': 'analysis',
        'note': 'Annualized run rate, not lifetime cashflow. Redacted step-ups and fees excluded.',
    }
    return result


def disclosed_pricing(doc):
    sections=section_index(doc)
    values=definitions(sections,'financing-agreement',['Applicable Rate'])
    if not values or values[0]['status']!='located':
        return {'status':'not_found','pricing_grid':[], 'note':'No uniquely located Applicable Rate definition in a financing agreement.'}
    definition=values[0];text=' '.join(s['evidence'] for s in definition['sources'])
    # Require the exact column convention; other table shapes fail closed.
    header=re.search(r'Commitment Fee\s+and ESTR Loans',text)
    if not header or 'EURIBOR Loans' not in text[:header.end()]:
        return {'status':'unresolved_table_layout','pricing_grid':[], 'sources':definition['sources']}
    rows=[]
    for m in re.finditer(r'\b(\d+)\s+([≥≤<>]?\s*[A-Z][A-Za-z0-9+\-/]*)\s+(\d+(?:\.\d+)?)%\s+(\d+(?:\.\d+)?)%',text[header.end():]):
        level,rating,fee,margin=m.groups()
        rows.append({'pricing_level':int(level),'debt_ratings_s_and_p_moodys_fitch':rating.strip(),
                     'commitment_fee_rate':float(fee)/100,'loan_margin_rate':float(margin)/100})
    if not rows or [r['pricing_level'] for r in rows]!=list(range(1,len(rows)+1)):
        return {'status':'unresolved_table_layout','pricing_grid':[], 'sources':definition['sources']}
    fees=[s for s in sections if s['layer']=='financing-agreement' and re.fullmatch(r'Fees\.?',s['title'])]
    redacted=[]
    if re.search(r'increased by an additional\s*\[\*+\]',text):redacted.append('margin_stepup_amount')
    for section in fees:
        for pattern,label in [(r'duration fee equal to\s*\[\*+\]','duration_fee_amount'),
                              (r'funding fee.{0,100}?equal to\s*\[\*+\]','funding_fee_amount')]:
            if re.search(pattern,section['text'],re.I):redacted.append(label)
    return {'status':'disclosed_grid','designation':'fact','review_status':'unreviewed',
            'benchmarks':['EURIBOR','ESTR'],'pricing_grid':rows,'sources':definition['sources'],
            'fee_sources':[x for s in fees for x in s['sources']],
            'redacted_components':sorted(set(redacted)),
            'limitations':['The borrower rating and current market benchmark are not established by this table.',
                          'Redacted amounts cannot be reconstructed from the public source. Fee Letter terms may be unavailable.',
                          'This is the base pricing grid, not a complete loan cashflow or default-interest model.']}
