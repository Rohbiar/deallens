"""Optional OpenAI Responses transport. No credentials enter audit outputs."""
import json
import os
import ssl
import time
import urllib.error
import urllib.request
import certifi
from .citations import source_id_request, resolve_citations, PROTOCOL, VALUE_PROTOCOL

SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {"proposals": {"type": "array", "maxItems": 20, "items": {
        "type": "object", "additionalProperties": False,
        "properties": {
            "field_name": {"type": "string"},
            "citations": {"type": "array", "minItems": 1, "maxItems": 12, "items": {
                "type": "object", "additionalProperties": False,
                "properties": {"chunk_id": {"type": "string"}, "evidence": {"type": "string"}},
                "required": ["chunk_id", "evidence"]}},
            "normalized_value_json": {"type": "string"},
            "raw_value": {"type": ["string", "null"]},
            "currency": {"type": ["string", "null"]},
            "value_qualifier": {"type": ["string", "null"], "enum": ["exact", "at_least", "at_most", None]},
            "confidence": {"type": "number"},
            "limitations": {"type": "string"}},
        "required": ["field_name", "citations", "normalized_value_json", "raw_value", "currency", "value_qualifier", "confidence", "limitations"]}}},
    "required": ["proposals"]}

class ProviderError(RuntimeError):
    """Safe-to-log transport error; excludes response body and credentials."""

GPT55_MODELS = {'gpt-5.5', 'gpt-5.5-2026-04-23'}


def build_request_body(request):
    """Shared transport and offline budget planning; never includes credentials."""
    payload, schema, passages, catalog_hash = source_id_request(request, SCHEMA)
    body = {"model": request["model"], "store": False,
            "instructions": request["system"],
            "input": json.dumps(payload, ensure_ascii=False),
            "max_output_tokens": 6000,
            "text": {"format": {"type": "json_schema", "name": "transaction_evidence", "strict": True, "schema": schema}}}
    if request["model"] in GPT55_MODELS:
        body["reasoning"] = {"effort": "medium"}
    return body, passages, catalog_hash

class OpenAIProvider:
    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, api_key=None, *, timeout=90, opener=None, sleeper=time.sleep, budget=None):
        self._key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self._key:
            raise ProviderError("Set OPENAI_API_KEY in your local environment before using --model. Never paste it into a document.")
        self.timeout = timeout
        # Do not forward an Authorization header through redirects.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None
        # Preserve system/custom trust and add a portable CA bundle. Some macOS
        # Python installers have no usable default CA file until separately set up.
        context = ssl.create_default_context()
        context.load_verify_locations(cafile=certifi.where())
        self.opener = opener or urllib.request.build_opener(
            NoRedirect(), urllib.request.HTTPSHandler(context=context)).open
        self.sleeper = sleeper
        self.last_metadata = {}
        self.budget = budget

    def __call__(self, request):
        self.last_metadata = {}
        body, passages, catalog_hash = build_request_body(request)
        # A bounded comparison should not multiply flagship costs on HTTP retries.
        attempts = 1 if request["model"] in GPT55_MODELS else 3
        encoded = json.dumps(body).encode()
        for attempt in range(attempts):
            reservation_id = self.budget.reserve(body) if self.budget else None
            req = urllib.request.Request(self.endpoint, data=encoded, headers={
                "Authorization": "Bearer " + self._key, "Content-Type": "application/json"}, method="POST")
            try:
                with self.opener(req, timeout=self.timeout) as response:
                    raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise ProviderError("Provider response exceeds size limit")
                data = json.loads(raw)
                if self.budget and isinstance(data,dict):
                    self.budget.record_usage(reservation_id, data.get('usage'))
                break
            except urllib.error.HTTPError as exc:
                if exc.code in {429, 500, 502, 503, 504} and attempt < attempts - 1:
                    self.sleeper(2 ** attempt)
                    continue
                raise ProviderError(f"Model provider returned HTTP {exc.code}; check configuration or quota locally.") from None
            except urllib.error.URLError as exc:
                if isinstance(exc.reason, ssl.SSLCertVerificationError):
                    raise ProviderError("TLS certificate verification failed; check the installed CA bundle or your network's approved trust configuration. Certificate verification remains enabled.") from None
                raise ProviderError("Model connection failed; check DNS, network access and proxy configuration. Completion and billing may be unknown. No automatic connection retry.") from None
            except TimeoutError:
                # A timed-out POST may have been billed; do not automatically duplicate it.
                raise ProviderError("Model request failed or timed out; its completion and billing may be unknown. No automatic timeout retry.") from None
            except (ValueError, UnicodeError):
                raise ProviderError("Provider returned invalid JSON") from None
        if not isinstance(data, dict):
            raise ProviderError("Provider returned an invalid response envelope")
        self.last_metadata = {"response_id": data.get("id"), "model": data.get("model"), "usage": data.get("usage"), "attempts": attempt + 1}
        self.last_metadata.update(citation_protocol=PROTOCOL, value_protocol=VALUE_PROTOCOL, passage_catalog_sha256=catalog_hash, passage_count=len(passages), reasoning=body.get("reasoning"), max_output_tokens=6000, attempt_limit=attempts)
        if self.budget:
            self.last_metadata['budget'] = self.budget.summary()
        if data.get("status") != "completed":
            raise ProviderError("Model response was incomplete; no partial extraction accepted")
        output = data.get("output")
        if not isinstance(output,list) or any(not isinstance(item,dict) for item in output):
            raise ProviderError("Provider returned invalid output items")
        parts = []
        for item in output:
            content = item.get("content", [])
            if not isinstance(content,list) or any(not isinstance(part,dict) for part in content):
                raise ProviderError("Provider returned invalid content items")
            parts.extend(content)
        if any(p.get("type") == "refusal" for p in parts):
            raise ProviderError("Model refused extraction; no output accepted")
        texts = [p.get("text") for p in parts if p.get("type") == "output_text"]
        if any(not isinstance(t,str) for t in texts):
            raise ProviderError("Provider returned invalid text content")
        text = "".join(texts)
        try:
            result = json.loads(text)
        except (ValueError, TypeError):
            raise ProviderError("Model response did not contain a valid extraction object") from None

        return resolve_citations(result, passages)
