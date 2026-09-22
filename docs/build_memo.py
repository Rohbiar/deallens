"""Render the three-page technical memo; requires reportlab, not needed by app."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab
import json

font_root = Path(reportlab.__file__).resolve().parent/'fonts'
pdfmetrics.registerFont(TTFont('DejaVu',str(font_root/'Vera.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuBold',str(font_root/'VeraBd.ttf')))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold')

ROOT=Path(__file__).resolve().parents[1]
run=json.loads((ROOT/'outputs/latest.json').read_text())['run_id']
runfolder=ROOT/'outputs'/run
case_metrics={d:json.loads((runfolder/d/'metrics.json').read_text()) for d in ('bio_techne','organon','uber_delivery_hero')}
case_terms={d:json.loads((runfolder/d/'structured_terms.json').read_text()) for d in ('bio_techne','organon','uber_delivery_hero')}
semantic=json.loads((ROOT/'docs/SEMANTIC_EVALUATION.json').read_text())['metrics']
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='MemoTitle',fontName='DejaVuBold',fontSize=21,leading=26,spaceAfter=14,textColor=colors.black))
styles.add(ParagraphStyle(name='MemoH',fontName='DejaVuBold',fontSize=11,leading=14,spaceBefore=11,spaceAfter=6,textColor=colors.black))
styles.add(ParagraphStyle(name='MemoBody',fontName='DejaVu',fontSize=9.5,leading=12.8,spaceAfter=7))
styles.add(ParagraphStyle(name='MemoSmall',fontName='DejaVu',fontSize=7.7,leading=10.5,spaceAfter=5))
story=[]
def p(text,style='MemoBody'):story.append(Paragraph(text,styles[style]))
def h(text):p(text,'MemoH')
def table(rows,widths):
    data=[[Paragraph(str(c),styles['MemoSmall']) for c in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf2')),('GRID',(0,0),(-1,-1),.45,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t);story.append(Spacer(1,9))

p('DealLens technical assessment','MemoTitle')
p('Mizuho Derivatives Risk Solutions | Public source prototype','MemoSmall')
p('DealLens links three public transaction filings to structured evidence, source comparisons and illustrative financing sensitivities. The final deterministic run adds recursive provision dependencies and 14 candidate structured terms containing 34 atomic statements. Those terms remain unreviewed and do not become facts, supported QA answers or analytics inputs. No human verification is claimed.')
h('Implementation and evidence controls')
p('Python ingestion preserves PDF hashes, page inventories, exhibit layers and page/character locators. A shared 42-field catalog drives scalar extraction. Numbered clauses expand through a bounded recursive same-instrument graph with stable source IDs, cycles, ambiguity and budget state. The same graph supplies displayed QA context and optional model requests.')
p('Structured candidates keep actors, modalities, triggers, conditions, exceptions, timing, scope and evidence separate. Material or unknown dependencies block support. Exact citation matching proves provenance, not interpretation. Organon and Uber filing dates are SEC-index-verified; Bio-Techne is PDF-metadata-reported. Omitted schedules and incorporated documents are not assumed available.')
table([['Document','Pages','Supported fields','Excerpt fields','Candidate terms']]+[[label,str(case_metrics[key]['page_count']),str(case_metrics[key]['machine_supported_fields'])+' of 42',str(case_metrics[key]['source_excerpt_fields']),str(len(case_terms[key]))] for label,key in [('Bio-Techne','bio_techne'),('Organon','organon'),('Uber / Delivery Hero','uber_delivery_hero')]],[125,42,105,90,85])
p('Supported counts exclude excerpts and candidates. All three sources use the same generic code. The validation sources informed shared improvements, so final results are adapted validation rather than pristine holdout accuracy.','MemoSmall')
h('Material source distinctions')
p('<b>Bio-Techne:</b> March 25, 2027 outside date with specified automatic extensions to June 25 and September 25; further written agreement can extend it again. The debt-issuance assumptions in the assignment are synthetic, not disclosed financing terms. [1]')
p('<b>Organon:</b> an elective extension can change the remedy obligations when Parent elects it. Award treatment also varies by grant year. Full sections preserve the grant-year cohorts, closing-time-condition exception and Parent-elected waiver for review. [2]')
p('<b>Uber:</b> a German public takeover, not a US merger. The summary price is EUR 41.50; the agreement specifies at least EUR 41.50. A EUR 11.5bn financing floor is distinct from the disclosed EUR 14.2bn bridge commitment. The model preserves these distinctions. [3]')

story.append(PageBreak())
p('Financing and hedge analysis','MemoTitle')
p('All figures below use the assignment\'s synthetic USD 4bn, seven-year fixed-rate issue and USD 65,000 DV01 per USD 100mm. Portfolio DV01 is USD 2.6mm per basis point. Positive net incremental cost is worse for the issuer; positive hedge P&amp;L is a receipt.')
h('Benchmark and spread decomposition')
p('Assumed bond coupon is Treasury plus issuer spread: 4.25% + 1.00% = 5.25%. The 4.40% swap rate implies a 15bp initial swap spread, which is not added again to the bond coupon. Debt cost sensitivity equals DV01 times the benchmark and issuer-spread moves. A payer swap follows the swap-rate move, leaving issuer-spread and swap-spread basis risk. Credit DV01 is assumed equal to benchmark DV01.')
table([['Scenario','Unhedged','Payer swap','Payer option','Contingent swap'],['Benchmark +25bp','65','0','12','8'],['Benchmark -25bp','-65','0','-53','8'],['Benchmark +50bp','130','0','12','8'],['Benchmark +25bp and credit +20bp','117','52','64','60'],['Neutral transaction failure','0','0','12','8']],[160,70,75,80,83])
p('Values are USD millions of incremental cost PV. Option premium is a synthetic 30bp of notional (USD 12mm); the contingent swap fee is a synthetic 20bp (USD 8mm), paid upfront in every outcome. Both assume matching hedge DV01. These are scenario assumptions, not market prices or executable terms.','MemoSmall')
h('Failure and timing')
p('The required neutral failure scenario applies no market shock. Separate failure-up and failure-down sensitivities show that a conventional payer swap can create an unwind receipt or payment. An ordinary payer option retains its independent payoff; a deal-contingent swap cancels without settlement while retaining its fee. No transaction termination fee is automatically offset against hedge loss.')
p('Delay scenarios use hypothetical closing on an explicitly stated extension date with separately labeled roll or renewal costs. They do not assert that extension conditions have been met. A +25bp rate move changes annual coupon cost by USD 10mm, distinct from the USD 65mm PV sensitivity; these measures are never summed. Outcome-weighted results depend on an explicitly synthetic joint rate/completion distribution.')
h('Validation adaptations')
p('Organon uses a synthetic USD 1bn fixed-rate refinancing slice because the baseline does not establish a supported issuance size and tenor. Uber uses a synthetic EUR 1bn slice plus separate FX and floating-bridge sensitivities. The bridge commitment is not assumed fully drawn, and its 364-day floating exposure does not use the seven-year bond DV01. A six-level disclosed bridge grid is now separate from assumed draw and EURIBOR. Step-up amounts, duration fees and funding fees are publicly redacted; no missing amount is inferred. [2, 3]')

story.append(PageBreak())
p('Validation and next steps','MemoTitle')
h('Verification evidence')
p('The project passes 179 unit/control tests, 25/25 selected scalar/source fixtures and 18/18 provision fixtures. The frozen agent-curated semantic set contains 72 supported assertions and four deliberately unresolved cases. Current candidate-only predictions asserted zero values: precision is null, recall is 0, all 72 supported assertions are unresolved and all four source-unresolved cases were respected.')
p('Tests cover evidence graphs, financial identities, structured actors and modalities, unresolved dependencies, malformed model output, stale review and escaped rendering. Integration review fixed a generic named-party capture, statement-level unresolved analytics gating and the Uber award clause selector. Passing these tests does not establish full legal recall, and no human decisions are fabricated.')
h('Current scope and remaining work')
p('Across 36 required transaction/question combinations, 12 answers are supported, 22 partial, one conflicted and one review-required. Complex answers expose full provisions, structured components and unresolved reasons but do not count as completed legal interpretation. Conditional events never appear as having occurred. The neutral failure scenario is distinct from directional failure stresses.')
p('The final deterministic run made no provider calls and preserved historical budget records. Bio-Techne filing-date provenance, omitted Bio-Techne and Organon schedule content, ambiguous Uber award outcomes and redacted Uber bridge fees remain open. Contract-wide semantic precision and recall and human legal review remain unavailable; the candidate retains ownership of the code, calculations and disclosures.')

h('Production and confidential information')
p('For material non-public information, use firm-approved isolated infrastructure, authenticated deal-level access, private model endpoints, restricted egress, encrypted storage and approved retention terms. Reapply source permissions at retrieval and output. Keep credentials in a secrets service. Document text has no authority to execute tools or transmit data. Material corrections and distribution require attributed human approval; trading remains outside this application.')
p('Replace illustrative prices with approved curves and volatility surfaces, add exact bridge cashflows and FX pricing, and reconcile against independent pricing tools. Add authenticated, signed review events, reproducible dependency locks, source-update monitoring and broader exception handling before operational deployment.')
h('Primary source references')
p('[1] Bio-Techne Form 8-K and merger agreement, supplied PDF: summary pp. 1-3; Sections 4.07, 5.06 and 7.01, PDF pp. 46, 60 and 71-72. <link href="https://investors.bio-techne.com/all-sec-filings/content/0001999371-26-013527/0001999371-26-013527.pdf" color="#125c76">Original filing</link>.','MemoSmall')
p('[2] Organon Form 8-K and merger agreement, supplied PDF: summary pp. 2-4; financing discussion pp. 59-60; Section 9.2 pp. 86-87; Section 9.5 pp. 88-89. <link href="https://d18rn0p25nwr6d.cloudfront.net/CIK-0001821825/c7307cd7-fbd0-40af-acc9-3a591887131d.pdf" color="#125c76">Original filing</link>.','MemoSmall')
p('[3] Uber Form 8-K, BCA and bridge agreement, supplied PDF: summary pp. 2-4; BCA clauses 1.2, 1.4 and 1.5, pp. 13-15; bridge exhibit starts p. 44. <link href="https://d18rn0p25nwr6d.cloudfront.net/CIK-0001543151/b4fca6cb-0d5e-4b0c-93e8-f58c357d3b48.pdf" color="#125c76">Original filing</link>.','MemoSmall')

def footer(canvas,doc):
    canvas.setFont('DejaVu',8);canvas.setFillColor(colors.HexColor('#647583'))
    canvas.drawString(72,37,'DealLens | Public source research prototype')
    canvas.drawRightString(540,37,str(doc.page))

doc=SimpleDocTemplate(str(ROOT/'docs/TECHNICAL_MEMO.pdf'),pagesize=letter,rightMargin=72,leftMargin=72,topMargin=52,bottomMargin=55,title='DealLens technical assessment',author='Codex assisted project')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(ROOT/'docs/TECHNICAL_MEMO.pdf')
