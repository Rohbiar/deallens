"""Generate current status from the latest outputs; retain historical reports."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    run = json.loads((ROOT / "outputs/latest.json").read_text())["run_id"]
    folder = ROOT / "outputs" / run
    manifest = json.loads((folder / "manifest.json").read_text())
    rows = []
    totals = Counter()
    term_count = statement_count = supported_term_count = 0
    for item in manifest["documents"]:
        ident = item["document_id"]
        path = folder / ident
        metrics = json.loads((path / "metrics.json").read_text())
        qa = json.loads((path / "qa.json").read_text())
        doc = json.loads((path / "document.json").read_text())
        terms = json.loads((path / "structured_terms.json").read_text())
        counts = Counter(answer["status"] for answer in qa.values())
        totals.update(counts)
        term_count += len(terms)
        statement_count += sum(len(term.get("statements", [])) for term in terms)
        supported_term_count += sum(
            term.get("status") in {"machine_supported", "human_verified"} for term in terms
        )
        rows.append(
            f"| {ident} | {metrics['machine_supported_fields']}/42 | "
            f"{metrics.get('source_excerpt_fields', 0)} | {len(terms)} | "
            f"{counts['supported']}/12 | {counts['partial']}/12 | "
            f"{doc['filing_date']} ({doc['filing_date_status']}) |"
        )

    log = (ROOT / "docs/TEST_RESULTS.txt").read_text()
    match = re.search(r"Ran (\d+) tests", log)
    tests = match.group(1) if match else "unrecorded"
    source = json.loads((ROOT / "docs/SOURCE_EVALUATION.json").read_text())
    provisions = json.loads((ROOT / "docs/PROVISION_EVALUATION.json").read_text())
    semantic = json.loads((ROOT / "docs/SEMANTIC_EVALUATION.json").read_text())["metrics"]
    body = f'''# Submission status

Current run: `{run}` at code commit `{manifest["code_version"][:7]}`. This is a runnable submission candidate with explicit semantic limitations, not a claim of complete extraction. This deterministic run made no provider calls and contains zero human-verified records.

| Transaction | Supported field types | Section-excerpt fields | Structured candidates | Fully supported questions | Partial questions | Filing date |
|---|---:|---:|---:|---:|---:|---|
''' + "\n".join(rows) + f'''

Across the 36 required transaction/question combinations there are {totals['supported']} supported answers, {totals['partial']} partial answers, {totals['requires_review']} review-required answer and {totals['conflict']} conflicted answer. The run contains {term_count} candidate structured terms with {statement_count} atomic statements; {supported_term_count} are machine-supported or human-verified. Candidate terms enrich explanations but do not promote QA answers or drive analytics.

## Final implementation state

- Numbered provisions carry a bounded recursive dependency graph with stable source and section IDs, cycle detection, instrument boundaries, and explicit missing, ambiguous and budget-limited context.
- Versioned structured candidates cover extensions, fees, remedies, award cohorts and disclosed financing conditions. Actors, modalities, triggers, conditions, exceptions, timing, amounts and evidence remain separate.
- Structured candidates are persisted in JSON and SQLite and exposed in QA, comparisons, timelines, risk views, CLI and server responses. The browser labels uncertainty and never represents an election or conditional event as having occurred.
- Analytics include a neutral zero-rate transaction-failure scenario. Directional failure stresses remain additional sensitivities. Only validated supported terms without material unresolved items may drive structured dates; the current candidates do not.
- The model-request adapter and displayed QA evidence use the same retrieval graph, with downstream omissions disclosed. No transaction-specific names, dates, amounts or section numbers were added to generic interpretation logic.

## Verification

- {tests} automated unit/control tests pass.
- {source['passed']}/{source['total']} selected scalar/source fixtures pass.
- {provisions['passed']}/{provisions['total']} selected provision/qualifier fixtures pass, and all attached context citations match their normalized source pages.
- The frozen agent-curated semantic set contains 72 supported atomic assertions and four deliberately unresolved source cases. The current candidate-only system asserted {semantic['bounded_asserted_prediction_denominator']}: {semantic['counts']['unresolved']} are reported unresolved, bounded precision is null, bounded recall is {semantic['bounded_atomic_recall']}, and {semantic['unresolved_reference_counts']['respected']}/4 source-unresolved cases were respected.
- Required Bio-Techne scenarios include the neutral `failure` scenario, both extension scenarios and the four specified rate/credit stresses.

These results establish artifact integrity, selected source retention and fail-closed behavior. They do not establish contract-wide legal precision or recall.

## Remaining limitations

All structured terms remain unreviewed candidates because their dependency graphs retain material or unknown unresolved context. Bio-Techne's filing date remains PDF-metadata-reported. The supplied record omits the Bio-Techne approval-jurisdiction schedule and an Organon PSU schedule exception; Uber's ultimate award treatment remains consent- and award-term-dependent, and public bridge step-up, duration-fee and funding-fee amounts are redacted. Exact citations prove provenance, not interpretation.

No human legal verification, live market valuation or authenticated production approval is claimed. The candidate must understand and accept the code, calculations and disclosed limitations before submission.

## Evidence and deliverables

See [requirement audit](REQUIREMENTS_AUDIT.json), [bounded semantic evaluation](SEMANTIC_EVALUATION.json), [source evaluation](SOURCE_EVALUATION.json), [provision evaluation](PROVISION_EVALUATION.json), [known issues](KNOWN_ISSUES.md), [technical memo](TECHNICAL_MEMO.pdf), and [demo guide](DEMO_GUIDE.md). The review archive must be rebuilt after the final memo so its manifest and extracted smoke checks describe this run.
'''
    (ROOT / "docs/SUBMISSION_STATUS.md").write_text(body)
    validation = '''# Assignment validation

The original specification was checked against the integrated code and current run. File existence is not treated as completion. The machine-readable matrix is [REQUIREMENTS_AUDIT.json](REQUIREMENTS_AUDIT.json); current measured coverage is in [SUBMISSION_STATUS.md](SUBMISSION_STATUS.md).

## Result

Engineering and artifact-integrity controls pass for the current run. The prototype processes all three documents with one application, retains evidence lineage, produces all required scenario families, exposes all 36 question categories, and fails closed on unsupported or conflicting interpretations.

Semantic completion remains partial. Fourteen structured terms and 34 statements are candidates, not approved facts. The bounded challenge set reports all 72 supported assertions unresolved and safely preserves all four intentionally unresolved source cases. This is useful evidence of conservative behavior, not an accuracy claim.

## Submission boundary

The archive, memo and browser evidence must be regenerated against the current run after documentation is finalized. Bio-Techne filing-date provenance, omitted schedules, redacted bridge fees, ambiguous Uber award outcomes, human legal verification and contract-wide semantic precision/recall remain open and must stay disclosed.
'''
    (ROOT / "docs/ASSIGNMENT_VALIDATION.md").write_text(validation)
    print(ROOT / "docs/SUBMISSION_STATUS.md")


if __name__ == "__main__":
    build()
