# Source review and interview discussion points

This review identifies material terms observed directly in the three supplied PDFs and explains why they matter to the prototype. It is an agent-authored review aid, not a complete legal opinion or a record of human verification. Physical PDF page numbers are used throughout. These observations are not hard-coded into the application's answers.

## Bio-Techne and Merck KGaA

**Structure and parties.** The June 25, 2026 agreement is a cash merger involving Bio-Techne, Merck KGaA and EMD Holdings NewCo, Inc. Bio-Techne survives as Parent's subsidiary. The filing's earliest-event date is June 23, which is not the signing date. The stock consideration is USD 73 per share, subject to the stated exclusions and withholding provisions. Shareholder approval is based on a majority of voting power of outstanding shares entitled to vote. Sources: filing summary, PDF pages 1–2; agreement preamble, page 10; Section 2.01, page 12.

**Timing.** The initial outside date is March 25, 2027. Regulatory-related conditions can trigger automatic extensions to June 25 and September 25, 2027. Section 7.01 also permits further dates agreed in writing, so September 25 is the last specified automatic extension, not an absolute impossibility of further extension. Termination rights are qualified, including restrictions relating to a party's breach and enforcement proceedings. Sources: summary page 3; Section 7.01, pages 71–72.

**Equity awards.** Vested options cash out their positive intrinsic value; underwater or at-the-money options receive no consideration. Unvested options generally become cash-based awards retaining vesting terms, with unfinished performance conditions measured at target. RSUs and PSUs become cash-based awards; unfinished PSU performance is measured at maximum, not target. Restricted stock has its own treatment. Do not collapse all awards into an immediately payable acquisition cash amount. Sources: summary page 2; Section 2.03 begins on page 16 and continues on following pages.

**Fees.** The disclosed company termination fee is USD 230.455mm and parent termination fee USD 576.140mm. The company fee can arise from specified recommendation/superior-proposal events and a conditional competing-proposal tail of 12 months. The parent fee relates to specified regulatory termination outcomes and has qualifications. Neither fee is payable merely because any failure occurs. Sources: summary page 3; Section 7.02, pages 74–75.

**Financing and remedies.** Section 4.07 expressly states that obtaining financing is not a condition to closing or the specified obligations. This does not mean a financing facility has no lender conditions. Section 5.06(c) defines limits involving business sectors outside Parent's Life Science sector, a stated material-adverse-effect measure and specified future-transaction oversight obligations. Sources: agreement page 46 and page 60.

**Hedging implication.** The assignment's USD 4bn debt issue is synthetic. Use its debt DV01 for hedge sizing, not purchase price or termination fee. The modeled March 15 issuance predates the March 25 outside date; it is an assumption, not a source forecast. Review automatic extensions, permitted additional extensions and enforcement-related termination restrictions when choosing hedge expiry and a deal-contingent failure definition.

## Organon and Sun Pharma

**Structure and parties.** This is a US cash merger dated April 26, 2026. Parent is Sun Pharmaceutical Holdings USA, Inc.; Merger Sub is Sun Pharma America, Inc. Other named Sun Pharma entities participate for covered provisions. Avoid treating the ultimate Indian parent, the acquisition parent and guarantors as interchangeable. The consideration is USD 14 per share. Sources: summary page 2; agreement preamble page 13 and consideration definition page 25.

**Financing.** The filing discloses committed debt financing supplemented by other available funds to cover consideration and other obligations, including refinancing or repayment of certain existing debt. Section 6.10(e) states that Parent's obligations are not conditional on obtaining financing. The commitment letters and detailed financing uses require separate treatment. Sources: summary page 2; agreement pages 59–60. The model's USD 1bn seven-year fixed-rate slice is entirely synthetic and does not claim to be the debt commitment.

**Timing and changing risk.** Initial outside date: January 26, 2027 at 5 p.m. New York time. Either party may elect an extension to April 26, 2027 by the required written notice if the stipulated regulatory conditions remain outstanding while other conditions meet the contractual test. Critically, a Parent election modifies the referenced regulatory covenant and irrevocably waives the substantial-detriment condition to the stated extent. An election by the Company is not described as causing that same change. Sources: Section 9.2(a), pages 86–87. The baseline extracts the date but does not yet encode the whole election-dependent state transition.

**Equity awards.** Options, whether vested or unvested, generally cash out positive intrinsic value. Pre-2026 RSUs accelerate and cash out, while awards granted in 2026 or later generally become cash successor awards with continuing terms. Pre-2026 PSUs accelerate using target performance; later PSUs also use target performance for conversion but generally retain service-based requirements, with specified qualifying-termination protection. Sources: summary pages 2–3. Grant year and vesting/service status must be separate dimensions, not one generic “RSUs cash out” statement.

**Termination fee and tail.** The company termination fee is USD 120mm. Section 9.5 includes specific superior-proposal/recommendation triggers and a nine-month conditional acquisition-proposal tail; it should not inherit Bio-Techne's 12-month tail. Payment deadlines and proposal-threshold substitutions also matter. Sources: summary page 4; definition page 28; Section 9.5 pages 88–89. The absence of a normalized parent fee in this prototype is not evidence that the amount is zero.

**Hedging implication.** Separate debt-funding conditions from transaction conditions, and model both the closing-date change and altered remedy obligations when considering an extension. The legal event structure matters to a contingent hedge's cancellation terms and probability assumptions.

## Uber and Delivery Hero

**Structure.** This is a German voluntary public takeover offer governed by a Business Combination Agreement, not a conventional US merger. Uber International Technologies II Corporation is the Bidder; Delivery Hero is the target. The acceptance threshold includes shares held by or attributed to the Bidder and affiliates: at least 50% plus one share of the relevant outstanding share count, excluding treasury shares. The denominator and attributed holdings matter. Sources: summary pages 2–3; BCA clauses 1.1–1.2, pages 11–14.

**Price qualification.** The summary reports EUR 41.50 per share. Clause 1.4 requires cash consideration of at least EUR 41.50. Equal numeric amounts do not make those propositions identical. The comparison flags the exact-versus-minimum distinction and blocks a canonical answer until reviewed. Source: summary page 2 versus agreement page 15. This is a qualification difference, not a legal conclusion that the filing contradicts the contract.

**Deadlines.** The summary expects completion in the second half of 2027. Clause 1.2(b) uses November 10, 2027 for specified antitrust clearances, permits a later date authorized by BaFin, and caps that date at May 10, 2028, the defined long-stop date. Other conditions use the long-stop directly. The summary also describes a termination right tied to non-completion for regulatory reasons by the tenth business day after May 10 when the stated conditions apply. These are distinct events; none should simply become a US-style pair of automatic three-month extensions. Sources: summary pages 2–3; agreement page 13 and termination provisions.

**Financing amounts and credit structure.** The filing discloses a EUR 14.2bn senior unsecured bridge commitment, maturing 364 days after closing. Clause 1.5 separately contains a committed-financing floor of EUR 11.5bn under the stated certain-funds standard. These are different concepts, not two conflicting measurements of an identical field. Sources: summary page 4; agreement page 15; financing exhibit begins on page 44.

The disclosed bridge interest basis is EURIBOR plus a rating-dependent margin, with step-ups at days 90, 180 and 270. The summary describes a commitment fee beginning 120 days after the effective date, funding fees, duration fees and mandatory prepayments subject to exceptions. No borrowing had been drawn on the effective date. Financing availability and lender conditions require separate review, including the subsequent acceptance period and specified offer changes. Sources: summary page 4; financing agreement Section 4.02, page 89.

**Fees and remedies.** The company termination fee is EUR 200mm and the regulatory reverse fee EUR 700mm, with specific competing-offer/support and regulatory failure triggers. The summary describes the Bidder's reverse-fee obligation while the operative clause calls for Uber to pay or cause payment; payer identity should be preserved separately from the amount. The remedy limitation in clause 4.5 uses an adverse-and-material standard with specified business scope and excludes remedies not conditioned on completion. Sources: summary page 3; agreement pages 27 and 34–35.

**Hedging implication.** Separate floating EUR bridge risk, eventual fixed-rate refinancing risk and the currency mismatch of actual funding. Do not apply a seven-year bond DV01 to the whole 364-day floating bridge. A EUR purchase price alone does not prove the full amount needs an FX hedge. The model's 25% USD-funded share and all FX/bridge pricing parameters are synthetic illustrations.

## Questions to be ready to defend

1. Why can no financing condition coexist with conditional debt commitments?
2. Why does an exact price differ from a contractual floor, even at the same number?
3. Why is a long-stop date not an expected closing date or a guaranteed final deadline?
4. Which option or contingent-hedge terms determine the payout if the transaction fails?
5. What does the hedge leave exposed when the bond is priced over Treasury but the hedge is a swap?
6. Which award payments occur at closing versus later, and why does that affect funding size?
7. Why does a source-citation match not establish extraction accuracy?
8. What does this prototype fail to answer safely, and what review would unblock it?
