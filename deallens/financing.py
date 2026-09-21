"""Disclosed bridge pricing, separated from assumed draw and market levels."""
import re
from .provisions import section_index, definitions


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
