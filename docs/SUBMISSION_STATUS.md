# Submission status

Current run: `20260921T150631Z-5c182147`. This is a runnable submission candidate with explicit semantic limitations, not a claim of complete extraction. No provider calls were made in this continuation, and zero records are human-verified.

| Transaction | Supported field types | Additional section-excerpt fields | Fully supported questions | Partial questions | Filing date |
|---|---:|---:|---:|---:|---|
| bio_techne | 12/42 | 21 | 5/12 | 7/12 | 2026-06-26 (pdf_metadata_reported) |
| organon | 11/42 | 18 | 4/12 | 8/12 | 2026-04-27 (sec_index_verified) |
| uber_delivery_hero | 15/42 | 20 | 3/12 | 7/12 | 2026-07-16 (sec_index_verified) |

There are 12 fully supported answers, 22 partial answers, 1 review-required answers and 1 conflicted answers across the 36 required transaction/question combinations. Section excerpts are deliberately excluded from supported field counts. Partial answers provide full provisions and reference context; they are not completed legal interpretations.

## Changes in this continuation

- Added common numbered-section extraction across continuation pages, one-hop same-instrument references, selected defined-term expansion, and explicit missing/ambiguous/budget-limited context.
- Fixed RSU/pursuant and cure/procure substring retrieval errors. Added support for decimal headings with and without a trailing period and protection against table-of-contents matches.
- Exposed full contractual provisions in QA while keeping normalized values null and strict-mode abstention intact. Excerpts cannot be approved as an interpretation without an explicit correction.
- Added a source-backed six-level bridge pricing grid and annualized sensitivities using separately labeled assumed draw and EURIBOR. Identified redacted step-up, duration-fee and funding-fee amounts.
- Preserved business-day/calendar-day units and contractual anchors in relative timeline expressions. The risk map is now visible in the browser.
- Matched all three PDFs to fresh publisher downloads; pinned hashes and page counts. Verified Organon and Uber filing dates against SEC indexes; Bio-Techne remains explicitly PDF-metadata-reported.

## Verification

- 97 automated unit/control tests pass.
- 25/25 selected scalar/source fixtures pass.
- 18/18 selected complete-section/qualifier retention fixtures pass. All attached citations, including reference and definition context, match their normalized source pages.
- The disclosed bridge grid and redaction checks pass. These checks do not measure legal precision/recall, an independent valuation, or exhaustive clause recall.

## Remaining acceptance gaps

Complete structured interpretation of complex award cohorts, fee tails, remedy limits and conditional deadlines remains unfinished. Most complex questions now expose their full source sections, but the application does not assert that every exception has been reconciled. The Uber exact/minimum price difference and unsupported transaction financing-condition question remain safely unresolved.

The supplied public record omits some schedules and redacts some financial terms. Do not infer those values or treat their absence as an extraction failure that can be fixed with a guess. Independent semantic evaluation remains unavailable; fixtures are agent-curated, and the validation sources informed common improvements.

The final ownership task is to understand and accept the submitted code, calculations and disclosed limitations. No nominal legal attestation is requested. Production authentication, live pricing and enterprise deployment are future work, not prerequisites imposed by this prototype specification.

## Evidence and deliverables

See [requirement audit](REQUIREMENTS_AUDIT.json), [source metadata checks](SOURCE_METADATA_CHECKS.json), [section regression evidence](PROVISION_EVALUATION.json), [known issues](KNOWN_ISSUES.md), [technical memo](TECHNICAL_MEMO.pdf), and [demo guide](DEMO_GUIDE.md). `outputs/deliverables/DealLens_review_package.zip` is the review archive, with hashes and genuine Git history.
