# Model extraction and attributed review

The current deterministic run `20260922T024418Z-d989f939` made no provider calls and contains no model proposals or human approvals. Historical live evaluations and their persistent budget records remain preserved in older runs and dated reports.

## Optional bounded model extraction

Configure `OPENAI_API_KEY` privately and use an approved Responses API model supporting structured output:

```bash
python -m deallens.cli run --model YOUR_MODEL_ID --model-fields consideration_per_share financing_condition --max-model-calls 12
```

Each request covers one field and source layer under call, character, token and persistent monetary bounds. Requests have no tools and ask for no storage. Request hashes, retrieved source IDs, model identity and reported usage are audited; credentials are not logged.

For priority complex fields, the request adapter uses the same `retrieval-context/v1` sources displayed by QA. Any downstream truncation and omitted source IDs are recorded. Scalar fields retain the legacy chunk retriever. Source text is untrusted data and cannot authorize tools or change instructions.

Schema validation and exact citations establish format and provenance only. Model values remain candidates with null normalized values. They cannot set `review_status=verified`, create machine-supported structured terms or drive analytics.

## Structured interpretation boundary

The offline structured interpreter produces versioned candidate terms for extensions, fees, remedies, awards and financing conditions. It preserves actor, modality, trigger, conditions, exceptions, timing, amount, scope and statement-level source IDs. Validation checks shape, provenance, contradictions and unresolved dependencies.

Machine support requires an independent semantic basis and no material or unknown unresolved context at either term or statement level. The final 14 terms fail that gate safely. The frozen semantic adapter therefore emits unresolved predictions rather than laundering candidate content into supported assertions.

## Human review workflow

```bash
python -m deallens.cli review-export --out review_packet.json
# Inspect original PDFs and edit the packet locally.
python -m deallens.cli review-apply review_packet.json
```

The export contains no pre-approved decisions. A reviewer must provide an identity, explicit attestation, complete field/layer scope and a substantive reason. Approvals and corrections validate source hashes and evidence, create a new immutable run and preserve superseded records. Rejections also remain in history. Cross-layer conflicts are not erased.

The current review workflow governs legacy field records. It does not imply that candidate structured terms have been human-verified. Reviewer identity is local self-attestation, not authenticated enterprise approval. Strict QA continues to abstain in the supplied run.

## Current evaluation

- 179 unit/control tests pass.
- 25/25 selected scalar/source fixtures and 18/18 selected provision fixtures pass.
- The frozen agent-curated semantic set contains 72 supported atomic assertions and four intentionally unresolved cases.
- Current predictions assert zero values because every structured term is a candidate. Precision is null, recall is zero, all 72 supported assertions are unresolved and all four source-unresolved cases are respected.
- Zero records are human-verified, and the final structured wave made no paid provider calls.

Historical model reports document earlier provider behavior, citation failures and semantic errors. They must not be read as current-run coverage or human approval. The persistent reservation ledger must not be deleted or reset without new authorization.

## Production controls

Confidential use requires approved private endpoints, deal-level authorization, restricted egress, encrypted storage, managed secrets, approved retention and authenticated signed review. Reapply source permissions at retrieval and output. Human approval is required for material corrections or distribution; trading remains outside the application.
