# Model extraction and attributed review

Latest v5 evaluation: 18 responses, six candidates, eleven validation failures and one abstention; material semantic errors persist. See [FOCUSED_RETEST.md](FOCUSED_RETEST.md). V6 replaces model-written quotations with IDs selected from a request-specific source catalogue. The adapter reconstructs exact evidence and retains the existing integrity checks. This protocol passes offline tests but has not been evaluated live. No human approval is implied.

## Bounded model run

Configure `OPENAI_API_KEY` securely in your local shell and choose a Responses API model supporting structured output. Requests transmit retrieved public-source text to the provider and may incur charges. Only use approved data and credentials.

```bash
python -m deallens.cli run --model YOUR_MODEL_ID --model-fields consideration_per_share financing_condition --max-model-calls 12
```

The limit is per document, not per project. Each request covers one field/source layer, with at most 16,000 retrieved characters and 6,000 output tokens. Selected retryable HTTP failures allow up to three attempts per logical call. These size/call bounds operate alongside the persistent monetary reservation guard described below. Request hashes, retrieved chunk IDs, returned model identity and token usage are retained in `model_audit.json`; no API key is logged. Usage-based estimates are reported separately from reservations and actual billing.

Omit `--model-fields` to consider the common 42-field catalog. The default budget will not cover every field/layer. A budget of 126 permits up to 42 fields across three layers per document, but does not guarantee complete retrieval or accurate interpretation. Requests with no retrieved evidence abstain. Cross-page neighbors improve context, but definition chains and distant exceptions can still be missed.

Citation quotes must match supplied chunks and source pages exactly. This proves provenance only. Model values are held as `candidate_value` with null `normalized_value`, so downstream answers cannot silently promote them to facts. `store=false` is requested; this is not a guarantee of zero provider retention or approval for confidential data.

## Review workflow

```bash
python -m deallens.cli review-export --out review_packet.json
# Inspect original PDFs and edit the exported packet locally.
python -m deallens.cli review-apply review_packet.json
```

The UI also offers a review-packet download. Review is applied through the CLI; the browser remains read-only. The export has no pre-approved decisions. Keep its `base_run_id`, enter your real reviewer name and set `human_review_attested` to true only after doing the work. Add decisions such as this template, replacing every placeholder with the actual record scope and your own reasoning:

```json
{
  "document_id": "DOCUMENT_ID_FROM_PACKET",
  "field_name": "consideration_per_share",
  "document_layer": "transaction-agreement",
  "record_ids": ["RECORD_ID_FROM_PACKET"],
  "action": "approve",
  "complete_field_layer": true,
  "reason": "YOUR SOURCE-BASED REVIEW RATIONALE"
}
```

Approval requires a consistent existing candidate/supported value. Use `correct` with `normalized_value`, `currency` and `value_qualifier` when reconciling an interpretation; complex values may be JSON objects. Monetary corrections must occur with their currency and qualifier in the cited evidence. Date corrections must occur in the evidence. Use `reject` to exclude selected evidence without replacing it. A reject decision does not require `complete_field_layer`.

Approval/correction covers the entire field within that source layer: inspect all candidates, adjacent pages and referenced definitions before attesting completeness. Other active records in that field/layer become superseded, but remain in the audit history. Cross-layer conflicts are not erased by approving one layer. Only one decision per field/layer is allowed in a packet.

Applying a valid packet verifies the base run and PDF hashes, creates a new immutable run and regenerates comparison, QA, timeline, risk and analytics using the saved assumptions. The original run is preserved. Rejected/superseded records are excluded from downstream calculations and answers. Stale packets are rejected; export again after a successful review. `ask --strict` requires verified evidence, while still blocking conflicts and missing support.

Reviewer attribution is a local self-attestation, not authenticated identity or a signed approval. Test fixtures use fictional reviewers and temporary synthetic PDFs; they do not verify any shipped transaction record. Enterprise authentication, dual approval and tamper-resistant storage remain production work.

## Evaluation commands and current result

After any run, execute `python tests/evaluate_sources.py` and `PYTHONPATH=. python tests/evaluate_model.py`. The latter writes `docs/MODEL_EVALUATION.json`, separating retrieval excerpt hits, provider audit outcomes, reported usage, candidate matches and human verification. Matching a selected scalar fixture cannot validate complex awards, fees or all exceptions. Current baseline: 16/16 fixture excerpts retrieved, 76 provider responses, zero human approvals; complete semantic precision and recall remain null.

The 2026-09-20 continuation found no `OPENAI_API_KEY` in the task environment. The user plans to configure credentials and name a model. A shell export in another terminal may not propagate to the running app; run the bounded command in the configured shell if needed and then return its run ID for evaluation. Never paste the key into chat. No substitute model has been selected.

The transport follows the [official Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs). The continuation added safe handling of malformed response envelopes, non-finite nested proposal values and preceding context retrieval. Provider output remains unverified even when its schema and citations pass.

## TLS setup recovery

The first user-initiated live run (`20260920T161654Z-c7b3c412`) retained zero proposals after connection errors. A local probe identified missing trusted CA certificates. The transport now loads Certifi roots alongside default trust and reports certificate failures specifically; HTTPS certificate verification remains enabled. Install the updated pinned requirements when moving this project to another environment. A successful unauthenticated probe returned HTTP 401, confirming connectivity only. Rerun the bounded extraction in the terminal containing your exported key to test authentication and model output.

## Authorized $10 testing allowance

On 2026-09-20 the user authorized $10 for testing. CLI live runs now always use `outputs/api_budget.sqlite`: an atomic SQLite reservation ledger shared across documents and subsequent runs. $1 is held for earlier use and billing uncertainty, leaving $9 for new request reservations. This buffer is not claimed as actual historical spend. Each HTTP attempt reserves before sending; retry, timeout, crash and invalid-output reservations are never automatically refunded. Concurrent runs cannot both spend the same remaining allowance. Do not delete/reset the ledger without new authorization.

The local guard accepts only `gpt-4.1-mini` and its `2025-04-14` snapshot. Prices checked against [official model documentation](https://developers.openai.com/api/docs/models/gpt-4.1-mini) on 2026-09-20: $0.40/M input and $1.60/M output tokens. Reservation uses serialized request byte length plus 8,192 framing tokens, the 6,000 output-token maximum, and a 2x margin, with no caching discount. Unknown prices, tools and oversized requests are blocked. This is conservative local cost control, not the provider's account billing enforcement; it cannot control other applications, taxes or future price changes. Retain the account-side budget too.

Run the prepared batch in the terminal holding the exported key:

```bash
bash scripts/run_semantic_batch.sh
```

The batch selects 15 common fields on all three sources and pins the existing model snapshot. `BATCH_PLAN.json` is an offline plan: 76 calls with retrieved evidence, approximately $2.94 reserved without retries and $8.81 if every call makes three attempts, plus the $1 buffer. No paid calls were made to generate that plan. Progress is printed after each logical request. Model outputs remain candidates requiring review. The API key is never stored in the script or budget ledger.

## Agent source inspection is not human approval

The user has stated that they cannot personally certify legal interpretations. The project therefore keeps agent source findings in `data/assessments/broad_batch.json`, bound to record and PDF hashes, and displays them as annotations only. They do not change review status or normalized values. No approval is required merely to document an agent finding. The human review CLI remains available for genuine qualified review; do not attest on behalf of the user.
