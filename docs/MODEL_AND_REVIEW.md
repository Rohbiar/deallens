# Model extraction and attributed review

The shipped outputs are an offline baseline. No live model run or actual human approval is claimed. The optional integration is tested through fake HTTP responses and synthetic evidence fixtures.

## Bounded model run

Configure `OPENAI_API_KEY` securely in your local shell and choose a Responses API model supporting structured output. Requests transmit retrieved public-source text to the provider and may incur charges. Only use approved data and credentials.

```bash
python -m deallens.cli run --model YOUR_MODEL_ID --model-fields consideration_per_share financing_condition --max-model-calls 12
```

The limit is per document, not per project. Each request covers one field/source layer, with at most 16,000 retrieved characters and 6,000 output tokens. Selected retryable HTTP failures allow up to three attempts per logical call. These are size/call bounds, not a monetary spending cap. Request hashes, retrieved chunk IDs, returned model identity and token usage are retained in `model_audit.json`; no API key is logged. No dollar-cost calculation is provided.

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

After any run, execute `python tests/evaluate_sources.py` and `PYTHONPATH=. python tests/evaluate_model.py`. The latter writes `docs/MODEL_EVALUATION.json`, separating retrieval excerpt hits, provider audit outcomes, reported usage, candidate matches and human verification. Matching a selected scalar fixture cannot validate complex awards, fees or all exceptions. Current baseline: 16/16 fixture excerpts retrieved, zero provider responses, zero human approvals; complete semantic precision and recall remain null.

The 2026-09-20 continuation found no `OPENAI_API_KEY` in the task environment. The user plans to configure credentials and name a model. A shell export in another terminal may not propagate to the running app; run the bounded command in the configured shell if needed and then return its run ID for evaluation. Never paste the key into chat. No substitute model has been selected.

The transport follows the [official Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs). The continuation added safe handling of malformed response envelopes, non-finite nested proposal values and preceding context retrieval. Provider output remains unverified even when its schema and citations pass.
