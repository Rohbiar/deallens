# DealLens: six dispatchable work packages

Prepared 2026-09-21. Baseline run: `20260921T150631Z-5c182147`. Read current code and reports before treating these baseline numbers as current: 97 automated tests, 25 selected scalar fixtures, 18 selected provision fixtures; supported field types 12/42, 11/42, 15/42; 12 fully supported answers out of 36. The other answers are partial, review-required or conflicted. This is not an accuracy estimate.

## Dispatch and integration order

- First wave: A (retrieval), D (evaluation reference set), and F's read-only requirements/documentation audit. B designs its schema before implementing against A's agreed interface.
- Second wave: B (structured interpretation) after A's contract is agreed; C can build consumers with synthetic fixtures once B's schema is agreed. E can independently audit current calculations and prepare financial tests.
- Third wave: C and E integrate B's actual outputs. D evaluates the integrated implementation using its frozen reference set.
- Final wave: F runs the integrated checks, updates documentation and builds the final archive. Other agents fix failures within their own files.

These are six work packages, not a requirement to run six agents simultaneously. If only a few agents are available, use the waves. Do not create isolated worktrees from an old commit: check the working tree first, preserve existing work and establish a shared baseline commit or equivalent snapshot. One coordinator integrates changes and owns shared-file wiring. Do not allow six agents to run packaging or move outputs/latest.json independently.

## Common instructions — include with every dispatch

Read README.md, EXECUTION_PLAN.md, AGENT_WORKFLOW.md, docs/ASSIGNMENT_REQUIREMENTS.txt, docs/SUBMISSION_STATUS.md, docs/KNOWN_ISSUES.md and docs/MODEL_AND_REVIEW.md. Primary source PDFs are in data/sources; the original assignment DOCX is available at /Users/rohitnambiar/Downloads/DealLens_Core_Case_Study_Editable.docx.

Use one reusable application. Do not put transaction names, source-specific section numbers, amounts or dates into generic extraction logic; specific expected values belong in attributed evaluation fixtures. Preserve original PDFs, historical runs, review decisions and API reservations. Do not copy credentials into artifacts. No paid API calls in these assignments: the last reported remaining conservative allowance is only $0.720034, shared across all agents, not per agent. Prepare requests or offline test fixtures if needed and report the estimate to the coordinator.

Exact citations establish provenance, not correctness. Agent/model assessments are not human review. Do not set review_status=verified or silently promote model confidence to support. Keep original candidate values and disclose any corrections. Source excerpts, semantic interpretations, assumptions and calculations must remain distinct. Missing schedules/redacted values remain unresolved; never fabricate them to improve coverage. Production authentication, live pricing and independent expert sign-off are not additional mandatory prototype requirements.

Each agent may edit only its owned files and new uniquely named modules/tests/report below. Request coordinator integration for shared files. Do not modify another agent's tests or reports. Run targeted meaningful tests; the coordinator runs the full suite and refreshes generated reports once integrated. Report actual measured work time if tracked; do not invent historical timing.

Return: changed files and commit/diff, interface changes, test commands/results, source pages examined, before/after coverage with its scope, unresolved issues and exact integration steps. Passing tests must not be presented as complete semantic accuracy.

## A — Complete clause retrieval and dependency context

**Dispatch prompt:** Extend the existing source-section retrieval in deallens/provisions.py. Do not replace it with a second retrieval pipeline. Inspect section_index, reference expansion, definitions and completeness reporting. Address missing subclauses, multi-reference expressions, cross-page continuations, definition dependencies, instrument boundaries, duplicate headings and truncation. Add bounded recursive expansion with cycle detection and an explicit unresolved-dependency list. Keep source ordering and physical-page locators. Connect the improved retrieval to semantic request construction only through a coordinator-reviewed adapter; source excerpts displayed in QA and context actually sent to the model must not silently diverge.

**Own:** deallens/provisions.py; new deallens/retrieval_context.py if useful; tests/test_provisions.py; new tests/test_retrieval_dependencies.py; docs/WORK_PACKAGE_A.md.

**Shared integration:** semantic.py request selection and citations.py passage construction remain coordinator-owned.

**Contract:** A context bundle exposes sources, section identifiers, reference/definition edges, unresolved reasons, truncation/budget state and source hash. Do not label a bundle globally complete merely because every recognized reference was found; unrecognized references remain a limitation. Agree the exact schema with B before implementation.

**Acceptance:** Existing provision tests pass. Add mutation tests for cycles, duplicate numbers in different instruments, missing schedules, references to multiple subsections and budget exhaustion. Demonstrate extension/fee clause continuations on all three supplied PDFs without document-specific extraction rules. Every attached excerpt revalidates against its source page. Report unresolved dependencies rather than silently dropping them.

## B — Structured interpretation of priority fields

**Dispatch prompt:** Build a reusable structured representation for complex provisions using A's context contract. Begin with extension_dates_and_conditions and fee_triggers_and_tails; complete these before expanding to remedy_limitations, award cohorts and financing conditions. Preserve the precise actor, action or obligation, beneficiary/payee where relevant, triggering event, conditions, exceptions, business scope, amount/currency/qualifier, time units and anchor, and statement-level evidence. Avoid flattening conditional clauses into a single string. Define a validation path that preserves unresolved interpretations and permits only specifically justified machine support. Do not globally auto-approve LLM output.

**Own:** new deallens/structured_terms.py; new deallens/term_validation.py; new tests/test_structured_terms.py; docs/WORK_PACKAGE_B.md.

**Shared integration:** Propose changes to catalog.py, model.py, semantic.py, extract.py, review.py and storage.py for coordinator integration. Preserve compatibility with historical records.

**Milestones:** B1 versioned schema and synthetic examples; B2 extensions and fees across three sources; B3 remedies; B4 awards/financing if time permits. State exactly which milestones are complete.

**Acceptance:** Distinguish automatic/elective extensions; Parent versus Company elections; required versus permitted versus prohibited remedies; fee payment deadlines versus subsequent-transaction tails; transaction financing conditions versus lender conditions. Missing material context blocks complete interpretation. Mutation tests must catch changed actors, omitted exceptions, wrong time units and contradictory values. Each supported structured assertion needs a documented basis beyond substring citation validation. Preserve candidate/null states where that basis is unavailable.

## C — QA, source comparisons, timeline and risk integration

**Dispatch prompt:** Consume B's versioned terms and A's context metadata in the existing QA and risk interface. Audit all 36 required transaction/question combinations. Present direct answers with field-level support and unresolved parts, rather than calling a full source section a completed interpretation. Preserve summary/agreement distinctions, conflicting values and strict-mode behavior. Use structured conditional events to improve timeline output without claiming an election occurred. Expose scope, prerequisites, actor and uncertainty in the browser.

**Own:** deallens/qa.py, deallens/risk.py, deallens/ui.html; new deallens/term_comparison.py and deallens/term_timeline.py; new tests/test_structured_qa.py; docs/WORK_PACKAGE_C.md.

**Shared integration:** Existing comparison/timeline functions in extract.py, bundle generation in cli.py and server.py response changes require coordinator integration.

**Acceptance:** Every required question has a tested status and evidence path. Unsupported responses retain the specified exact wording. A partial answer identifies missing components and does not appear fully supported. Narrative comparisons account for actors/conditions; uncertainty is not classified as a match. Conflicts and strict-mode exclusions remain effective. UI rendering escapes source/model text. Test actor-dependent extensions, conflicting prices and partial award cohorts. Do not force all 36 answers to supported when source evidence is absent.

## D — Semantic evaluation and independent challenge

**Dispatch prompt:** Independently inspect the source PDFs and freeze a small, high-value semantic reference set before evaluating B's outputs. Focus on extensions, fee triggers/tails, remedy limits and award cohorts across all three transactions. Use atomic assertions: actor, obligation, trigger, exception, timing, scope and source location. Record source uncertainty and omitted schedules. Keep this work separate from implementation choices; evaluate the final outputs only after expectations are recorded.

**Own:** new tests/semantic_reference.json; new tests/evaluate_semantics.py; new tests/test_semantic_evaluator.py; docs/WORK_PACKAGE_D.md. Do not rewrite existing scalar fixtures to make outputs pass.

**Acceptance:** Suggested bounded first set: at least one source-backed case per priority family per transaction where disclosed, plus missing/redacted/ambiguous cases. Report coverage, incorrect assertions, omissions, abstentions and unresolved cases separately. Any precision/recall has an explicit finite denominator and applies only to that reference set. Test the evaluator with seeded wrong actors, flipped modality, wrong tail periods and missing qualifiers. Cite physical pages and reproducible excerpts. Label references agent-curated, not human gold. If another model reviews them, preserve disagreements and identify it as machine assessment. Do not spend API allowance or upload documents externally without coordinator instruction.

## E — Reconcile transaction terms with financial analysis

**Dispatch prompt:** Audit the existing analytics and disclosed financing extraction before adding features. Preserve the assignment's synthetic Bio-Techne assumptions, seven required scenarios and distinct hedge payoffs. Inspect financing.py's disclosed bridge grid and redaction handling. Integrate B's structured timing/funding facts through an explicit facts-to-scenario mapping, keeping scenario elections and market inputs synthetic. Improve the explanation of how completion, delay, remedy obligations and financing conditions affect hedge choice; unsupported conclusions remain labeled analysis with limitations.

**Own:** deallens/analytics.py, deallens/financing.py; tests/test_disclosed_financing.py; new tests/test_term_scenario_mapping.py; docs/WORK_PACKAGE_E.md.

**Shared integration:** Coordinate config/assumptions.json and cli.py changes; do not alter contractual extraction in another agent's files.

**Acceptance:** Reconcile all required scenarios and sign conventions; distinguish PV from annual coupon expense, commitment from drawn balance, fixed-rate DV01 from floating bridge exposure, and transaction fees from hedge breakage. No double counting of benchmark, swap spread or issuer spread. Derive expected results independently in tests. Conditional extensions remain hypothetical until elected/triggered; missing dates use labeled assumptions or block the affected scenario. Redacted pricing stays unavailable. Explain any schema or output changes needed by C.

## F — Final requirement audit, reproducibility and submission

**Dispatch prompt:** Start with a read-only requirement-to-evidence inventory against the original DOCX. Track each requirement as implemented, partial, unsupported by source, or not implemented, with concrete evidence and a closure criterion. Do not equate file existence with completion. After A–E integrate, reconcile all status documents, run the full verification suite, regenerate the three-document outputs and final artifacts, and test the extracted archive independently. Preserve genuine Git history and list any uncommitted changes honestly.

**Own:** README.md, EXECUTION_PLAN.md, AGENT_WORKFLOW.md; docs/ASSIGNMENT_VALIDATION.md, docs/SUBMISSION_STATUS.md, docs/KNOWN_ISSUES.md, docs/GENERALIZATION.md, docs/DEMO_GUIDE.md, docs/build_status.py, docs/build_memo.py, docs/package_deliverables.py; tests/evaluate_requirements.py. Leave A–E's reports owned by their authors.

**Dependencies and controls:** Only F/coordinator may regenerate outputs/latest.json, consolidated runs, global evaluation reports, memo and archive, and only after integration. Use the relevant PDF skill for memo authoring/render verification. Existing original PDFs and prior run directories remain immutable. Check source metadata gaps, especially Bio-Techne's PDF-metadata-only filing date; preserve confidence in the provenance rather than assuming it is SEC-verified.

**Acceptance:** Full test and targeted evaluation results match the packaged code/run. Three transactions are present; lineage and assumption hashes reproduce; no credentials, virtual environments or fabricated review decisions are included. Memo is at most three pages and visually inspected. Restore/run the archive in an isolated directory using documented setup; test QA, source links, scenarios and audit export. Include a short demo and a candid limitations list. Record real workflow decisions, available timing and leverage estimates without inventing measurements. Final status explicitly separates code/control completion, source availability and semantic validation. Do not submit or publish externally.

## Coordinator-only completion gate

Accept each package with evidence, integrate shared files, and resolve cross-package inconsistencies before the final run. Keep model candidates and machine-supported records distinct from human approval. A technically passing build cannot close unresolved extraction requirements. Deliver one current requirement matrix, one reproducible three-document run, one consistent memo/archive, and a concrete list of any remaining substantive limitations. Optional external review is useful evidence, not a substitute for these gates.
