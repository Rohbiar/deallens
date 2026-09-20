"""Render the three-page technical memo; requires reportlab, not needed by app."""
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold')

ROOT=Path(__file__).resolve().parents[1]
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='MemoTitle',fontName='DejaVuBold',fontSize=21,leading=26,spaceAfter=14,textColor=colors.black))
styles.add(ParagraphStyle(name='MemoH',fontName='DejaVuBold',fontSize=11,leading=14,spaceBefore=11,spaceAfter=6,textColor=colors.black))
styles.add(ParagraphStyle(name='MemoBody',fontName='DejaVu',fontSize=9.5,leading=13.2,spaceAfter=8))
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
p('DealLens links three public transaction filings to evidence, source comparisons and illustrative financing sensitivities. It is a reviewable baseline, not complete legal extraction. Bounded model extraction and versioned review are implemented, but no live-model evaluation or actual human verification has occurred. Complex clauses remain unresolved.')
h('Implementation and evidence controls')
p('Python ingestion preserves PDF hashes, page inventories, exhibit layers and page/character locators. A common 42-field catalog drives scalar extraction and bounded model proposals with exact citation checks. Explicit review decisions create new runs and regenerate dependent outputs; prior runs are preserved. SQLite retains request and review events. Reviewer identity is self-attested. The browser is read-only and loopback-bound.')
p('Relevant executed agreements outrank summaries, but conflicting values and qualifiers are retained. Exact evidence matching proves provenance, not semantic correctness. Complex provisions return null normalized values and enter the review queue. Actual filing dates and external page completeness remain unverified; neither is inferred from signing dates or internal page counts.')
table([['Document','Pages','Supported field types','Human verified'],['Bio-Techne','99','9 of 42','0'],['Organon','109','8 of 42','0'],['Uber and Delivery Hero','149','11 of 42','0']],[170,55,125,118])
p('A supported field count means at least one source layer has a machine-supported value; it does not imply complete subfields or a resolved canonical comparison. All three sources use the same code. Common rules were revised after validation inspection, so the final results are adapted validation results, not pristine holdout accuracy.','MemoSmall')
h('Material source distinctions')
p('<b>Bio-Techne:</b> March 25, 2027 outside date with specified automatic extensions to June 25 and September 25; further written agreement can extend it again. The debt-issuance assumptions in the assignment are synthetic, not disclosed financing terms. [1]')
p('<b>Organon:</b> an elective extension can change the remedy obligations when Parent elects it. Award treatment also varies by grant year. Neither distinction is adequately represented by a single date or generic award description. [2]')
p('<b>Uber:</b> a German public takeover, not a US merger. The summary price is EUR 41.50; the agreement specifies at least EUR 41.50. A EUR 11.5bn financing floor is distinct from the disclosed EUR 14.2bn bridge commitment. The model preserves these distinctions. [3]')

story.append(PageBreak())
p('Financing and hedge analysis','MemoTitle')
p('All figures below use the assignment\'s synthetic USD 4bn, seven-year fixed-rate issue and USD 65,000 DV01 per USD 100mm. Portfolio DV01 is USD 2.6mm per basis point. Positive net incremental cost is worse for the issuer; positive hedge P&amp;L is a receipt.')
h('Benchmark and spread decomposition')
p('Assumed bond coupon is Treasury plus issuer spread: 4.25% + 1.00% = 5.25%. The 4.40% swap rate implies a 15bp initial swap spread, which is not added again to the bond coupon. Debt cost sensitivity equals DV01 times the benchmark and issuer-spread moves. A payer swap follows the swap-rate move, leaving issuer-spread and swap-spread basis risk. Credit DV01 is assumed equal to benchmark DV01.')
table([['Scenario','Unhedged','Payer swap','Payer option','Contingent swap'],['Benchmark +25bp','65','0','12','8'],['Benchmark -25bp','-65','0','-53','8'],['Benchmark +50bp','130','0','12','8'],['Benchmark +25bp and credit +20bp','117','52','64','60'],['Failure and benchmark -25bp','0','65','12','8']],[160,70,75,80,83])
p('Values are USD millions of incremental cost PV. Option premium is a synthetic 30bp of notional (USD 12mm); the contingent swap fee is a synthetic 20bp (USD 8mm), paid upfront in every outcome. Both assume matching hedge DV01. These are scenario assumptions, not market prices or executable terms.','MemoSmall')
h('Failure and timing')
p('A conventional payer swap can require an unwind payment when the deal fails after rates fall. An ordinary payer option can still pay on a failure scenario with higher rates; a deal-contingent swap is assumed to cancel without settlement on failure, retaining the fee. The two strategies are therefore modeled separately. No transaction termination fee is automatically offset against hedge loss.')
p('Delay scenarios use hypothetical closing on an explicitly stated extension date with separately labeled roll or renewal costs. They do not assert that extension conditions have been met. A +25bp rate move changes annual coupon cost by USD 10mm, distinct from the USD 65mm PV sensitivity; these measures are never summed. Outcome-weighted results depend on an explicitly synthetic joint rate/completion distribution.')
h('Validation adaptations')
p('Organon uses a synthetic USD 1bn fixed-rate refinancing slice because the baseline does not establish a supported issuance size and tenor. Uber uses a synthetic EUR 1bn slice plus separate FX and floating-bridge sensitivities. The bridge commitment is not assumed fully drawn, and its 364-day floating exposure does not use the seven-year bond DV01. Actual fee grids, day counts and lending conditions remain for review. [2, 3]')

story.append(PageBreak())
p('Validation and next steps','MemoTitle')
h('Verification evidence')
p('The project passes 48 unit/control tests and 16 selected source fixtures. Tests cover financial identities, evidence integrity, qualifiers, unsupported QA, bounded fake-provider requests, stale reviews and synthetic end-to-end review regeneration. Rejected/superseded records are excluded downstream. Fixtures were curated by the same agent; no full-document semantic accuracy percentage or live-model performance is claimed.')
p('Initial failures exposed an ancillary-agreement date contaminating the signing date and an outside-date proviso missed by the parser. Both resulted in common rule changes and regression tests. The agent log records these corrections, implementation decisions and genuine Git stages. No human decisions or live-model test results are fabricated.')
h('Required before submission')
p('Run and evaluate the implemented model integration with approved credentials, then complete actual review decisions. Reconcile party roles, fee triggers and tails, award cohorts, remedy qualifications, cross-references and acceptance mechanics. Resolve narrative summary/agreement comparisons and independently validate every material answer. Uber\'s regulatory deadline and long-stop structure must be modeled separately from US-style extension scenarios, which remain blocked.')
p('Expand the gold set with independent review and separate precision, recall and abstention. Preserve exact/minimum/maximum qualifiers and distinguish facility commitments from financing floors. A fail-closed prototype is preferable to unsupported completeness, but abstention alone does not meet the case\'s extraction objectives.')
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
