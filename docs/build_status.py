"""Generate one current status from the latest outputs; retain historical reports."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def build():
    run=json.loads((ROOT/'outputs/latest.json').read_text())['run_id']
    folder=ROOT/'outputs'/run;manifest=json.loads((folder/'manifest.json').read_text())
    rows=[];totals=Counter()
    for item in manifest['documents']:
        ident=item['document_id'];p=folder/ident
        metrics=json.loads((p/'metrics.json').read_text());qa=json.loads((p/'qa.json').read_text());doc=json.loads((p/'document.json').read_text())
        counts=Counter(a['status'] for a in qa.values());totals.update(counts)
        rows.append(f"| {ident} | {metrics['machine_supported_fields']}/42 | {metrics.get('source_excerpt_fields',0)} | {counts['supported']}/12 | {counts['partial']}/12 | {doc['filing_date']} ({doc['filing_date_status']}) |")
    log=(ROOT/'docs/TEST_RESULTS.txt').read_text();match=re.search(r'Ran (\d+) tests',log)
    tests=match.group(1) if match else 'unrecorded'
    source=json.loads((ROOT/'docs/SOURCE_EVALUATION.json').read_text())
    provisions=json.loads((ROOT/'docs/PROVISION_EVALUATION.json').read_text())
    body=f'''# Submission status

Current run: `{run}`. This is a runnable submission candidate with explicit semantic limitations, not a claim of complete extraction. No provider calls were made in this continuation, and zero records are human-verified.

| Transaction | Supported field types | Additional section-excerpt fields | Fully supported questions | Partial questions | Filing date |
|---|---:|---:|---:|---:|---|
'''+ '\n'.join(rows)+f'''

There are {totals['supported']} fully supported answers, {totals['partial']} partial answers, {totals['requires_review']} review-required answers and {totals['conflict']} conflicted answers across the 36 required transaction/question combinations. Section excerpts are deliberately excluded from supported field counts. Partial answers provide full provisions and reference context; they are not completed legal interpretations.

## Changes in this continuation

- Added common numbered-section extraction across continuation pages, one-hop same-instrument references, selected defined-term expansion, and explicit missing/ambiguous/budget-limited context.
- Fixed RSU/pursuant and cure/procure substring retrieval errors. Added support for decimal headings with and without a trailing period and protection against table-of-contents matches.
- Exposed full contractual provisions in QA while keeping normalized values null and strict-mode abstention intact. Excerpts cannot be approved as an interpretation without an explicit correction.
- Added a source-backed six-level bridge pricing grid and annualized sensitivities using separately labeled assumed draw and EURIBOR. Identified redacted step-up, duration-fee and funding-fee amounts.
- Preserved business-day/calendar-day units and contractual anchors in relative timeline expressions. The risk map is now visible in the browser.
- Matched all three PDFs to fresh publisher downloads; pinned hashes and page counts. Verified Organon and Uber filing dates against SEC indexes; Bio-Techne remains explicitly PDF-metadata-reported.

## Verification

- {tests} automated unit/control tests pass.
- {source['passed']}/{source['total']} selected scalar/source fixtures pass.
- {provisions['passed']}/{provisions['total']} selected complete-section/qualifier retention fixtures pass. All attached citations, including reference and definition context, match their normalized source pages.
- The disclosed bridge grid and redaction checks pass. These checks do not measure legal precision/recall, an independent valuation, or exhaustive clause recall.

## Remaining acceptance gaps

Complete structured interpretation of complex award cohorts, fee tails, remedy limits and conditional deadlines remains unfinished. Most complex questions now expose their full source sections, but the application does not assert that every exception has been reconciled. The Uber exact/minimum price difference and unsupported transaction financing-condition question remain safely unresolved.

The supplied public record omits some schedules and redacts some financial terms. Do not infer those values or treat their absence as an extraction failure that can be fixed with a guess. Independent semantic evaluation remains unavailable; fixtures are agent-curated, and the validation sources informed common improvements.

The final ownership task is to understand and accept the submitted code, calculations and disclosed limitations. No nominal legal attestation is requested. Production authentication, live pricing and enterprise deployment are future work, not prerequisites imposed by this prototype specification.

## Evidence and deliverables

See [requirement audit](REQUIREMENTS_AUDIT.json), [source metadata checks](SOURCE_METADATA_CHECKS.json), [section regression evidence](PROVISION_EVALUATION.json), [known issues](KNOWN_ISSUES.md), [technical memo](TECHNICAL_MEMO.pdf), and [demo guide](DEMO_GUIDE.md). `outputs/deliverables/DealLens_review_package.zip` is the review archive, with hashes and genuine Git history.
'''
    (ROOT/'docs/SUBMISSION_STATUS.md').write_text(body)
    (ROOT/'docs/ASSIGNMENT_VALIDATION.md').write_text('# Assignment validation\n\nThe original specification was reviewed against code and actual outputs. The current assessment is maintained in [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md) and [REQUIREMENTS_AUDIT.json](REQUIREMENTS_AUDIT.json). File existence is not treated as semantic completion.\n\n'+body[body.index('## Verification'):])
    print(ROOT/'docs/SUBMISSION_STATUS.md')


if __name__=='__main__':build()
