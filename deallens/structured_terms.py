"""Versioned, JSON-safe records for complex transaction provisions.

The schema preserves atomic statements and their evidence.  Constructing one of
these records does not make it correct, supported, or human verified.
"""
from copy import deepcopy
from hashlib import sha256
import json
import re


SCHEMA_VERSION = "structured-terms/v1"
CONTEXT_SCHEMA_VERSION = "retrieval-context/v1"

PRIORITY_FIELDS = {
    "extension_dates_and_conditions",
    "fee_triggers_and_tails",
    "remedy_limitations",
    "award_cohort_differences",
    "financing_conditions",
}
INTERPRETED_FIELDS = frozenset(PRIORITY_FIELDS)

STATEMENT_KINDS = {
    "extension",
    "fee_trigger",
    "fee_tail",
    "remedy",
    "award_treatment",
    "financing_condition",
}

MODALITIES = {"automatic", "required", "permitted", "prohibited", "conditional"}
TERM_STATUSES = {"candidate", "unresolved", "machine_supported", "human_verified"}
UNRESOLVED_MATERIALITIES = {"material", "non_material", "unknown"}

DATE_EXPRESSION = (
    r"(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+\d{1,2},\s+\d{4}|\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|September|October|"
    r"November|December)\s+\d{4}"
)
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "eighteen": 18, "twenty-four": 24,
}
ROLE_PARTY = r"(?:the\s+)?(?:Company|Parent|Bidder|Acquiror|Purchaser|Buyer|Seller)"
NAMED_PARTY = (
    r"(?-i:[A-Z][A-Za-z0-9&.'’\-]*"
    r"(?:\s+(?:[A-Z][A-Za-z0-9&.'’\-]*|SE|N\.V\.|Inc\.|Ltd\.)){0,3})"
)
PARTY_EXPRESSION = rf"(?:{ROLE_PARTY}|{NAMED_PARTY})"


def stable_id(prefix, value):
    """Return a stable identifier without treating array order as identity."""
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False).encode()
    return f"{prefix}-{sha256(encoded).hexdigest()[:16]}"


def evidence_ref(source_id, *, purpose="support"):
    return {"source_id": source_id, "purpose": purpose}


def party(name, role, *, aliases=(), resolution="resolved"):
    return {"name": name, "role": role, "aliases": list(aliases),
            "resolution": resolution}


def condition(condition_id, text, *, evidence=(), status="stated"):
    return {"condition_id": condition_id, "text": text, "status": status,
            "evidence": list(evidence)}


def timing(*, clock_type, value=None, unit=None, anchor=None, conditions=(),
           evidence=()):
    """Represent a date or clock without resolving conditional events."""
    return {"clock_type": clock_type, "value": value, "unit": unit,
            "anchor": anchor, "conditions": list(conditions),
            "evidence": list(evidence)}


def amount(value, currency, qualifier="exact", *, evidence=()):
    return {"value": value, "currency": currency, "qualifier": qualifier,
            "evidence": list(evidence)}


def statement(kind, actor, action, *, statement_id=None, beneficiary=None,
              trigger=None, conditions=(), exceptions=(), business_scope=None,
              amount_value=None, timing_value=None, evidence=(), unresolved=()):
    """Build one atomic assertion; all conditional components stay separate."""
    value = {
        "statement_id": statement_id,
        "kind": kind,
        "actor": deepcopy(actor),
        "action": deepcopy(action),
        "beneficiary": deepcopy(beneficiary),
        "trigger": deepcopy(trigger),
        "conditions": deepcopy(list(conditions)),
        "exceptions": deepcopy(list(exceptions)),
        "business_scope": deepcopy(business_scope),
        "amount": deepcopy(amount_value),
        "timing": deepcopy(timing_value),
        "evidence": deepcopy(list(evidence)),
        "unresolved": deepcopy(list(unresolved)),
    }
    if statement_id is None:
        identity = {k: value[k] for k in ("kind", "actor", "action", "beneficiary",
                                          "trigger", "business_scope")}
        value["statement_id"] = stable_id("stmt", identity)
    return value


def unresolved(reason, expression, *, dependency_id=None, materiality="unknown",
               evidence=()):
    return {"reason": reason, "expression": expression,
            "dependency_id": dependency_id, "materiality": materiality,
            "evidence": list(evidence)}


def term_record(field_name, context_bundle, statements, *, status="candidate",
                interpretation_method="unreviewed_candidate", unresolved_items=(),
                validation_basis=(), term_id=None):
    """Create a structured candidate bound to an immutable retrieval context."""
    record = {
        "schema_version": SCHEMA_VERSION,
        "term_id": term_id,
        "field_name": field_name,
        "document_id": context_bundle.get("document_id"),
        "document_sha256": context_bundle.get("source_hash"),
        "document_layer": _single_layer(context_bundle),
        "context": {
            "schema_version": context_bundle.get("schema_version"),
            "source_hash": context_bundle.get("source_hash"),
            "root_section_ids": list(context_bundle.get("root_section_ids", [])),
            "section_ids": list(context_bundle.get("section_ids", [])),
        },
        "status": status,
        "interpretation_method": interpretation_method,
        "statements": deepcopy(list(statements)),
        "unresolved": deepcopy(list(unresolved_items)),
        "validation_basis": deepcopy(list(validation_basis)),
        "review_status": "verified" if status == "human_verified" else "unreviewed",
    }
    if term_id is None:
        identity = {k: record[k] for k in ("schema_version", "field_name",
                                           "document_id", "document_sha256",
                                           "context", "statements")}
        record["term_id"] = stable_id("term", identity)
    return record


def _single_layer(context_bundle):
    layers = {section.get("document_layer")
              for section in context_bundle.get("sections", [])
              if section.get("section_id") in context_bundle.get("root_section_ids", [])}
    return next(iter(layers)) if len(layers) == 1 else None


def interpret_term(field_name, context_bundle):
    """Interpret a priority provision from a Package A context bundle.

    This deterministic pass deliberately produces candidates, not approvals. It
    recognizes a bounded legal-clause grammar and retains the source IDs used by
    each atomic statement. Retrieval gaps are copied into the term's unresolved
    list, so citation matches cannot make incomplete context look complete.
    """
    interpreters = {
        "extension_dates_and_conditions": _interpret_extensions,
        "fee_triggers_and_tails": _interpret_fees,
        "remedy_limitations": _interpret_remedies,
        "award_cohort_differences": _interpret_awards,
        "financing_conditions": _interpret_financing_conditions,
    }
    if field_name not in INTERPRETED_FIELDS:
        raise ValueError(f"no structured interpreter for {field_name}")
    sources = _root_sources(context_bundle)
    statements = interpreters[field_name](sources)
    open_items = _context_unresolved(context_bundle)
    if not statements:
        open_items.append(unresolved(
            "no_recognized_atomic_statement", field_name, materiality="material",
            evidence=[evidence_ref(s["source_id"]) for s in sources],
        ))
    return term_record(
        field_name, context_bundle, statements,
        status="candidate" if statements else "unresolved",
        interpretation_method="deterministic_clause_grammar/v1",
        unresolved_items=open_items,
        validation_basis=["clause_grammar", "statement_level_source_ids"],
    )


def _root_sources(bundle):
    roots = set(bundle.get("root_section_ids", []))
    return [source for source in bundle.get("sources", [])
            if source.get("section_id") in roots]


def _windows(sources):
    """Yield one- and two-span windows, retaining exact source attribution."""
    for index, source in enumerate(sources[:-1]):
        following = sources[index + 1]
        if following.get("section_id") == source.get("section_id"):
            yield (source.get("evidence", "") + " " + following.get("evidence", "")), [source, following]
    for index, source in enumerate(sources):
        yield source.get("evidence", ""), [source]


def _refs(window_sources):
    return [evidence_ref(source["source_id"]) for source in window_sources]


def _condition(text, refs, prefix):
    cleaned = " ".join(text.split()).strip(" ,;:")
    return condition(stable_id(prefix, cleaned), cleaned, evidence=refs)


def _party_from_text(value, role=None):
    name = " ".join(value.split()).strip(" ,;:")
    lower = name.lower()
    if role is None:
        if lower in {"the company", "company", "target"}:
            role = "company"
        elif lower in {"the parent", "parent"}:
            role = "parent"
        elif lower in {"the bidder", "bidder"}:
            role = "bidder"
        elif "either parent or the company" in lower:
            role = "either_party"
        elif "parent and the company" in lower or lower == "parties":
            role = "joint_parties"
        elif lower == "bafin":
            role = "regulator"
        else:
            role = "named_party"
    return party(name, role)


def _date_timing(value, refs, *, anchor=None, conditions=()):
    return timing(clock_type="absolute", value=value, unit="date", anchor=anchor,
                  conditions=conditions, evidence=refs)


def _interpret_extensions(sources):
    results = []
    seen = set()
    automatic = re.compile(
        rf"(?P<subject>(?:the\s+)?(?:First Extended\s+)?"
        rf"(?:Outside|Long-Stop) Date)\s+shall automatically extend to\s+"
        rf"(?P<date>{DATE_EXPRESSION})", re.I,
    )
    elective = re.compile(
        rf"(?P<actor>either\s+Parent\s+or\s+the\s+Company|Parent|the\s+Company|Company)\s+"
        rf"may,?\s+(?P<notice>by\s+written notice\s+to\s+the\s+other\s+Party[^,;]*),?\s*"
        rf"elect to extend\s+(?P<object>the\s+(?:Outside|Long-Stop) Date)\s+until\s+"
        rf"(?P<date>{DATE_EXPRESSION})", re.I,
    )
    joint = re.compile(
        rf"(?P<object>(?:the\s+)?(?:Outside|Long-Stop) Date)\s+may be further extended\s+"
        rf"(?:from time to time\s+)?to\s+(?P<date>such date)\s+as may be agreed in writing\s+"
        rf"between\s+(?P<parties>[^,;.]+)", re.I,
    )
    regulator = re.compile(
        rf"(?P<date>{DATE_EXPRESSION}),?\s+or\s+such later date\s+that may be authorized by\s+"
        rf"(?P<actor>[A-Z][A-Za-z]+),?\s+provided\s+in no event shall such date extend beyond\s+"
        rf"(?P<cap>{DATE_EXPRESSION})", re.I,
    )
    for text, window_sources in _windows(sources):
        refs = _refs(window_sources)
        for match in automatic.finditer(text):
            key = ("automatic", match.group("subject").lower(), match.group("date"))
            if key in seen:
                continue
            seen.add(key)
            prefix = text[max(0, match.start() - 1400):match.start()]
            condition_matches = list(re.finditer(
                r"if(?:\s+at\s+[^,;]+)?\s+all of the conditions to Closing,.{20,1200}?"
                r"(?:satisfied|capable of being satisfied)(?:\s+at such time)?", prefix, re.I,
            ))
            if condition_matches:
                condition_text = condition_matches[-1].group()
            else:
                starts = [m.start() for m in re.finditer(r"\bif\b", prefix, re.I)]
                condition_text = prefix[starts[-1]:] if starts else "stated extension conditions"
            condition_value = _condition(condition_text, refs, "condition")
            following = text[match.end():match.end() + 1800]
            exception_values = []
            exception_match = re.search(
                r"provided further,? that\s+(.{20,1000}?shall not be permitted to terminate.{20,900}?)"
                r"(?=;\s*\([ivx]+\)|$)", following, re.I,
            )
            if exception_match:
                exception_values.append(_condition(exception_match.group(1), refs, "exception"))
            results.append(statement(
                "extension", party("Operation of provision", "automatic_mechanism"),
                {"modality": "automatic", "verb": "extend", "object": match.group("subject")},
                trigger={"event": "extension conditions satisfied", "evidence": refs},
                conditions=[condition_value],
                exceptions=exception_values,
                timing_value=_date_timing(match.group("date"), refs,
                                          anchor=match.group("subject"),
                                          conditions=[condition_value["condition_id"]]),
                evidence=refs,
            ))
        for match in elective.finditer(text):
            key = ("elective", match.group("actor").lower(), match.group("date"))
            if key in seen:
                continue
            seen.add(key)
            notice = _condition(match.group("notice"), refs, "condition")
            prefix = text[max(0, match.start() - 1600):match.start()]
            prerequisites = []
            prerequisite_matches = list(re.finditer(
                r"if\s+on or prior to\s+.{20,1400}?all other conditions.{20,500}?"
                r"(?:satisfied|waived|capable of being satisfied).{0,160}?then\s*$",
                prefix, re.I,
            ))
            if prerequisite_matches:
                prerequisites.append(_condition(prerequisite_matches[-1].group(), refs,
                                                "condition"))
            following = text[match.end():match.end() + 1500]
            consequences = [
                _condition(found.group(1), refs, "exception")
                for found in re.finditer(
                    r"provided,?\s+further,?\s+that\s+(.{20,850}?)(?=;\s*provided|;\s*\([a-z]\)|$)",
                    following, re.I,
                )
            ]
            results.append(statement(
                "extension", _party_from_text(match.group("actor")),
                {"modality": "permitted", "verb": "elect to extend",
                 "object": match.group("object")},
                trigger={"event": "stated extension prerequisites satisfied", "evidence": refs},
                conditions=prerequisites + [notice], exceptions=consequences,
                timing_value=_date_timing(match.group("date"), refs,
                                          anchor=match.group("object"),
                                          conditions=[notice["condition_id"]]),
                evidence=refs,
            ))
        for match in joint.finditer(text):
            key = ("joint", match.group("parties").lower())
            if key in seen:
                continue
            seen.add(key)
            results.append(statement(
                "extension", _party_from_text(match.group("parties"), "joint_parties"),
                {"modality": "permitted", "verb": "agree in writing to extend",
                 "object": match.group("object")},
                trigger={"event": "written agreement between named parties", "evidence": refs},
                timing_value=timing(clock_type="conditional", value=None, unit=None,
                                    anchor=match.group("object"), evidence=refs),
                evidence=refs,
            ))
        for match in regulator.finditer(text):
            key = ("regulator", match.group("actor").lower(), match.group("cap"))
            if key in seen:
                continue
            seen.add(key)
            cap = _condition(f"in no event beyond {match.group('cap')}", refs, "exception")
            prefix = text[max(0, match.start() - 700):match.start()]
            after_publication = re.search(
                r"After publication of the Offer Document.{20,650}$", prefix, re.I,
            )
            conditions = ([_condition(after_publication.group(), refs, "condition")]
                          if after_publication else [])
            results.append(statement(
                "extension", _party_from_text(match.group("actor"), "regulator"),
                {"modality": "permitted", "verb": "authorize later date",
                 "object": "regulatory approvals and related conditions deadline"},
                trigger={"event": "after publication of offer document", "evidence": refs},
                conditions=conditions, exceptions=[cap],
                timing_value=_date_timing(match.group("cap"), refs,
                                          anchor=match.group("date")),
                evidence=refs,
            ))
    return results


def _sentence_condition(text, refs, prefix="condition"):
    """Retain a bounded operative fragment without pretending to normalize it."""
    return _condition(text[:1800], refs, prefix)


def _interpret_remedies(sources):
    """Recognize required remedy efforts and their express contractual limits."""
    results = []
    seen = set()
    for text, window_sources in _windows(sources):
        refs = _refs(window_sources)

        # Positive covenant followed by an expressly defined adverse-effect cap.
        substantial = re.search(
            r"(?P<actors>(?:the\s+)?Company\s+and\s+Parent|Parent\s+and\s+(?:the\s+)?Company)"
            r".{0,2600}?proffer,\s+agree to take and take any Remedial Action"
            r"\s+to the extent necessary to satisfy (?P<trigger>the condition.{0,80}?)\s*;"
            r"(?P<limit>.{80,3200}?Substantial Detriment\b)", text, re.I,
        )
        if substantial:
            key = ("substantial", substantial.group("actors").lower())
            if key not in seen:
                seen.add(key)
                following = text[substantial.end():substantial.end() + 1800]
                exceptions = [_sentence_condition(substantial.group("limit"), refs, "exception")]
                for match in re.finditer(r"provided,?\s+however,?\s+that\s+(.{30,1500})(?=\.\s+\([ivx]+\)|$)", following, re.I):
                    exceptions.append(_sentence_condition(match.group(1), refs, "exception"))
                results.append(statement(
                    "remedy", _party_from_text(substantial.group("actors"), "joint_parties"),
                    {"modality": "required", "verb": "take remedial action",
                     "object": "regulatory remedy"},
                    trigger={"event": "necessary to satisfy regulatory closing condition",
                             "evidence": refs},
                    exceptions=exceptions,
                    business_scope={"scope": "assets, operations, rights, product lines, licenses, businesses or interests",
                                    "limit": "Substantial Detriment"},
                    evidence=refs,
                ))

        # An affirmative remedy covenant limited by a competent authority demand.
        authority = re.search(
            r"(?P<actor>The\s+[A-Z][A-Za-z]+s?|The\s+Acquirors|Acquirors)\s+shall.{0,500}?"
            r"use best efforts.{0,900}?offering and accepting (?P<object>any remedies or conditions.{0,500}?)"
            r"if and up to the extent (?P<trigger>the competent authority.{20,300}?remedies or conditions),"
            r"\s*provided that (?P<limit>nothing in this Agreement.{30,1000})", text, re.I,
        )
        if authority:
            key = ("authority", authority.group("actor").lower())
            if key not in seen:
                seen.add(key)
                results.append(statement(
                    "remedy", _party_from_text(authority.group("actor"), "acquiror"),
                    {"modality": "required", "verb": "use best efforts to offer or accept remedy",
                     "object": "regulatory remedy or condition"},
                    trigger={"event": "competent authority would grant clearance only subject to remedy",
                             "evidence": refs},
                    exceptions=[_sentence_condition(authority.group("limit"), refs, "exception")],
                    business_scope={"scope": "business and assets identified by the clause",
                                    "limit": "adverse-and-material and completion-condition limits"},
                    timing_value=timing(clock_type="event_relative", value=None, unit=None,
                                        anchor="before stated transaction deadline", evidence=refs),
                    evidence=refs,
                ))

        # A negative covenant that defines a Burdensome Condition boundary.
        burdensome = re.search(
            r"nothing in this Agreement shall (?:obligate or )?require\s+"
            r"(?P<actors>Parent,\s+Merger Sub or any of their respective Affiliates|.{1,180}?)\s+"
            r"to take.{0,500}?if (?P<limits>such action.{80,2600}?Burdensome Condition.{0,3}\))", text, re.I,
        )
        if burdensome:
            key = ("burdensome", burdensome.group("actors").lower())
            if key not in seen:
                seen.add(key)
                results.append(statement(
                    "remedy", _party_from_text(burdensome.group("actors"), "protected_parties"),
                    {"modality": "prohibited", "verb": "require remedy beyond limit",
                     "object": "Burdensome Condition"},
                    trigger={"event": "proposed remedy meets a stated Burdensome Condition limb",
                             "evidence": refs},
                    exceptions=[_sentence_condition(burdensome.group("limits"), refs, "exception")],
                    business_scope={"scope": "specified businesses and post-closing combined enterprise",
                                    "limit": "Burdensome Condition"},
                    evidence=refs,
                ))
    return results


def _award_statement(refs, *, award_type, cohort, action_text, performance=None,
                     exceptions=(), timing_value=None, unresolved_items=()):
    scope = {"award_type": award_type, "cohort": cohort}
    if performance:
        scope["performance_measurement"] = performance
    return statement(
        "award_treatment", party("Operation of provision", "automatic_mechanism"),
        {"modality": "automatic", "verb": action_text,
         "object": f"{cohort} {award_type}"},
        trigger={"event": "Effective Time", "evidence": refs},
        exceptions=exceptions, business_scope=scope, timing_value=timing_value,
        evidence=refs, unresolved=unresolved_items,
    )


def _interpret_awards(sources):
    """Preserve grant-year, vesting and performance-measurement cohorts."""
    results = []
    seen = set()
    for text, window_sources in _windows(sources):
        refs = _refs(window_sources)

        for match in re.finditer(
            r"each (?:outstanding )?(?P<award>restricted stock unit|performance (?:share|stock) unit)"
            r".{0,100}?granted (?P<cohort>prior to calendar year (?P<year>\d{4})|in calendar year \d{4} or later)"
            r".{0,1200}?(?P<treatment>accelerate.{0,220}?(?:terminated and.{0,80}?cancelled)|"
            r"assumed by Parent and converted into a cash-based.{0,180}?award)", text, re.I,
        ):
            award_type = "PSU" if "performance" in match.group("award").lower() else "RSU"
            cohort = "pre_grant_year" if "prior to" in match.group("cohort").lower() else "grant_year_or_later"
            local_cohort = text[match.start():match.end() + 1800]
            performance_match = re.search(
                r"(?:based on|achieved at) (target|maximum|actual) performance",
                local_cohort, re.I,
            )
            performance = performance_match.group(1).lower() if performance_match else None
            key = (award_type, cohort, match.group("year"))
            if key in seen:
                continue
            seen.add(key)
            following = text[match.end():match.end() + 1600]
            exceptions = []
            for clause in re.finditer(r"provided(?:,?\s+however)?,?\s+that\s+(.{20,1000}?)(?=\.\s|;\s*provided|$)", following, re.I):
                exceptions.append(_sentence_condition(clause.group(1), refs, "exception"))
            unresolved_items = []
            # Only attach an omitted schedule if it occurs inside the matched
            # cohort treatment, not in a later award cohort in the same window.
            schedule = re.search(r"subject to (Section .{1,80}?Disclosure Schedule)", match.group(), re.I)
            if schedule:
                unresolved_items.append(unresolved("omitted_schedule", schedule.group(1),
                                                   materiality="material", evidence=refs))
            cohort_year = match.group("year") or re.search(r"\d{4}", match.group("cohort")).group()
            results.append(_award_statement(
                refs, award_type=award_type,
                cohort=f"{cohort}:{cohort_year}",
                action_text=("accelerate, cancel and cash out" if "accelerate" in match.group("treatment").lower()
                             else "assume and convert to cash-based award"),
                performance=performance, exceptions=exceptions,
                unresolved_items=unresolved_items,
            ))

        # Performance periods, rather than grant years, may define the cohort.
        for match in re.finditer(
            r"(?P<award>Company Option|PSU Award|Company Restricted Stock Award).{0,1200}?"
            r"performance period (?:that )?has not been completed.{0,220}?"
            r"(?:conditions shall be deemed to have been achieved at|based on) (?P<level>target|maximum|actual) performance",
            text, re.I,
        ):
            award_type = ("PSU" if "PSU" in match.group("award") else
                          "option" if "Option" in match.group("award") else "restricted_stock")
            key = (award_type, "incomplete_performance_period", match.group("level").lower())
            if key in seen:
                continue
            seen.add(key)
            results.append(_award_statement(
                refs, award_type=award_type, cohort="incomplete_performance_period",
                action_text="convert to cash-based award",
                performance=match.group("level").lower(),
            ))

        # Some takeover agreements state efforts/elections rather than a fixed outcome.
        efforts = re.search(
            r"With respect to all outstanding equity-based awards.{0,1000}?"
            r"(?P<actor>[A-Z][A-Za-z0-9 .&'-]+?)\s+shall,\s+to the extent legally permissible.{0,2200}?"
            r"use reasonable best efforts.{0,1800}?(?P<performance>actual performance.{0,500}?from \d{4} onwards)",
            text, re.I,
        )
        if efforts and ("efforts", efforts.group("actor").lower()) not in seen:
            seen.add(("efforts", efforts.group("actor").lower()))
            results.append(statement(
                "award_treatment", _party_from_text(efforts.group("actor")),
                {"modality": "required", "verb": "use reasonable best efforts for cash settlement",
                 "object": "outstanding equity-based awards"},
                trigger={"event": "outstanding equity awards covered by provision", "evidence": refs},
                conditions=[_sentence_condition("to the extent legally permissible", refs)],
                exceptions=[_sentence_condition("beneficiary consent and underlying award terms may control", refs, "exception")],
                business_scope={"award_type": "options, RSUs, PSUs and other equity-based awards",
                                "cohort": "all outstanding awards",
                                "performance_measurement": "actual, or target for unmeasurable share-price performance from stated year"},
                evidence=refs,
                unresolved=[unresolved("beneficiary_consent_or_award_terms", "ultimate award outcome",
                                       materiality="material", evidence=refs)],
            ))
    return results


def _interpret_financing_conditions(sources):
    """Separate transaction-closing conditions from lender funding conditions."""
    results = []
    seen = set()
    for text, window_sources in _windows(sources):
        refs = _refs(window_sources)
        no_financing_condition = re.search(
            r"neither the availability, the terms nor the obtaining of the (?P<financing>Debt Financing|financing)"
            r".{0,120}?is in any manner a condition to the Closing", text, re.I,
        )
        if no_financing_condition and "transaction" not in seen:
            seen.add("transaction")
            results.append(statement(
                "financing_condition", party("Transaction parties", "transaction_parties"),
                {"modality": "prohibited", "verb": "condition closing on financing availability",
                 "object": no_financing_condition.group("financing")},
                trigger={"event": "Closing", "evidence": refs},
                business_scope={"condition_type": "transaction_closing_condition",
                                "financing_role": "not a closing condition"},
                evidence=refs,
            ))

        lender = re.search(
            r"The obligation of each Lender to (?P<verb>honor any Request for Borrowing|make Loans)"
            r"(?P<when>.{0,100}?) is subject (?:only )?to the satisfaction of the following conditions precedent"
            r"(?P<conditions>.{80,3600}?)(?=\n?\s*\d+\.\d+\s+[A-Z]|ARTICLE\s+[IVX]+|$)", text, re.I,
        )
        if lender:
            phase = "initial_borrowing" if "honor" in lender.group("verb").lower() else "post_closing_borrowing"
            if phase not in seen:
                seen.add(phase)
                condition_items = []
                for item in re.finditer(r"(?:^|\s)\([a-z]\)\s+(.{10,900}?)(?=\s+\([a-z]\)\s+|$)", lender.group("conditions"), re.I):
                    condition_items.append(_sentence_condition(item.group(1), refs))
                results.append(statement(
                    "financing_condition", party("Each Lender", "lender"),
                    {"modality": "conditional", "verb": "fund borrowing",
                     "object": phase},
                    beneficiary=party("Borrower", "borrower"),
                    trigger={"event": "request for borrowing", "evidence": refs},
                    conditions=condition_items,
                    business_scope={"condition_type": "lender_funding_condition",
                                    "funding_phase": phase},
                    timing_value=timing(clock_type="event_relative", value=None, unit=None,
                                        anchor="Closing Date" if phase == "initial_borrowing" else "Funding Date",
                                        evidence=refs),
                    evidence=refs,
                ))

        certain_funds = re.search(
            r"During the Certain Funds Period.{0,200}?unless (?P<exception>a Major Event of Default.{0,100}?),"
            r"\s*none of the (?P<actors>Lenders or the Administrative Agent) shall be entitled to.{0,100}?"
            r"(?P<rights>refuse to make any Loan.{30,1800}?)(?=provided that|$)", text, re.I,
        )
        if certain_funds and "certain_funds" not in seen:
            seen.add("certain_funds")
            results.append(statement(
                "financing_condition", _party_from_text(certain_funds.group("actors"), "lenders_and_agent"),
                {"modality": "prohibited", "verb": "exercise specified funding remedies",
                 "object": "refusal, termination, rescission, cancellation, setoff or counterclaim"},
                trigger={"event": "Certain Funds Period", "evidence": refs},
                conditions=[_sentence_condition("stated borrowing conditions are satisfied", refs)],
                exceptions=[_sentence_condition(certain_funds.group("exception"), refs, "exception")],
                business_scope={"condition_type": "lender_certain_funds_restriction",
                                "funding_phase": "Certain Funds Period"},
                evidence=refs,
            ))
    return results


def _number(value):
    value = value.lower().strip()
    if value.isdigit():
        return int(value)
    return NUMBER_WORDS.get(value)


def _clock(text, refs, *, anchor):
    match = re.search(
        r"(?:within|no later than)\s+(?:(?P<word>[A-Za-z-]+)\s+)?"
        r"(?:\((?P<digits>\d+)\)|(?P<plain>\d+))?\s*"
        r"(?P<unit>Business Days?|business days?|calendar days?|months?)", text, re.I,
    )
    if not match:
        if re.search(r"prior to or concurrently with|immediately prior to or concurrently with", text, re.I):
            return timing(clock_type="event_relative", value=0, unit="calendar_days",
                          anchor=anchor, evidence=refs)
        if re.search(r"promptly", text, re.I):
            return timing(clock_type="event_relative", value=None, unit=None,
                          anchor=anchor, evidence=refs)
        return None
    raw = match.group("digits") or match.group("plain") or match.group("word")
    value = _number(raw) if raw else None
    unit = "business_days" if "business" in match.group("unit").lower() else (
        "months" if "month" in match.group("unit").lower() else "calendar_days")
    return timing(clock_type="relative", value=value, unit=unit,
                  anchor=anchor, evidence=refs)


def _money_after(text, fee_name, refs):
    pattern = re.compile(
        rf"{re.escape(fee_name)}\s+(?:\([^)]*\)\s+)?shall amount to\s+"
        rf"(?P<currency>EUR|USD|GBP)\s+(?P<value>[\d,]+(?:\.\d+)?)", re.I,
    )
    match = pattern.search(text)
    if not match:
        return None
    return amount(float(match.group("value").replace(",", "")),
                  match.group("currency").upper(), evidence=refs)


def _interpret_fees(sources):
    results = []
    seen = set()
    seen_local_clauses = set()
    pay = re.compile(
        rf"(?P<payer>{PARTY_EXPRESSION})\s+"
        rf"shall\s+(?P<preamble>.{{0,180}}?)pay(?:,?\s+or cause to be paid,?)?\s+to\s+"
        rf"(?P<payee>{PARTY_EXPRESSION})"
        rf"(?:\s+or its designee)?\s+"
        rf"(?:the\s+)?(?P<fee>(?:Company\s+)?Termination Fee|Regulatory Reverse Fee|Parent Termination Fee)", re.I,
    )
    tail = re.compile(
        r"within\s+(?P<count>[A-Za-z-]+|\d+)\s+months?\s+after\s+"
        r"(?P<anchor>the date of any such termination|any such termination(?: and abandonment)?)"
        rf"(?P<trigger>.{{0,900}}?)then\s+(?P<payer>{PARTY_EXPRESSION})\s+"
        r"shall\s+(?:pay|pay or cause to be paid)(?P<payment>.{0,260}?)\s+to\s+"
        rf"(?P<payee>{PARTY_EXPRESSION})(?:\s+or its designee)?\s+"
        r"(?:the\s+)?(?P<fee>(?:Company\s+)?Termination Fee|Regulatory Reverse Fee|Parent Termination Fee)", re.I,
    )
    for text, window_sources in _windows(sources):
        refs = _refs(window_sources)
        for match in tail.finditer(text):
            count = _number(match.group("count"))
            key = ("tail", match.group("payer").lower(), match.group("fee").lower(), count)
            if key in seen:
                continue
            seen.add(key)
            trigger_text = " ".join(match.group("trigger").split()).strip(" ,;:")
            prefix = text[max(0, match.start() - 1500):match.start()]
            prerequisite = re.search(
                r"(?:If|In the event)\s+(.{30,1400})$", prefix, re.I,
            )
            conditions = ([_condition(prerequisite.group(), refs, "condition")]
                          if prerequisite else [])
            payment_text = " ".join(match.group("payment").split()).strip(" ,;:")
            if payment_text:
                conditions.append(_condition(f"payment mechanics: {payment_text}", refs,
                                             "condition"))
            following = text[match.end():match.end() + 700]
            qualifier = re.search(r"For purposes of\s+(.{20,620}?)(?=\.\s|$)", following, re.I)
            exceptions = ([_condition(qualifier.group(), refs, "exception")]
                          if qualifier else [])
            results.append(statement(
                "fee_tail", _party_from_text(match.group("payer")),
                {"modality": "required", "verb": "pay", "object": match.group("fee")},
                beneficiary=_party_from_text(match.group("payee"), "payee"),
                trigger={"event": trigger_text, "evidence": refs},
                conditions=conditions, exceptions=exceptions,
                timing_value=timing(clock_type="relative", value=count, unit="months",
                                    anchor="termination", evidence=refs),
                evidence=refs,
            ))
        for pattern in (pay,):
            for match in pattern.finditer(text):
                fee_name = match.group("fee")
                prefix = text[max(0, match.start() - 1500):match.start()]
                trigger_match = re.search(r"(?:In the event|If)\s+(.{20,650}?)(?:;\s*)?then\s*$", prefix, re.I)
                route_match = re.search(
                    r"(?:^|;\s*)(\([ivx]+\)\s+by\s+.{20,600}?)then\s*$", prefix, re.I,
                )
                trigger_text = (" ".join(trigger_match.group(1).split()) if trigger_match
                                else " ".join(route_match.group(1).split()) if route_match
                                else "payment obligation described by preceding termination clause")
                local = text[match.start():min(len(text), match.end() + 260)]
                normalized_local = " ".join(local.lower().split())
                clause_key = (match.group("payer").lower(), match.group("payee").lower(),
                              fee_name.lower(), normalized_local)
                if (trigger_text == "payment obligation described by preceding termination clause"
                        and clause_key in seen_local_clauses):
                    continue
                seen_local_clauses.add(clause_key)
                key = ("fee", match.group("payer").lower(), match.group("payee").lower(),
                       fee_name.lower(), trigger_text.lower(), normalized_local)
                if key in seen:
                    continue
                seen.add(key)
                results.append(statement(
                    "fee_trigger", _party_from_text(match.group("payer")),
                    {"modality": "required", "verb": "pay", "object": fee_name},
                    beneficiary=_party_from_text(match.group("payee"), "payee"),
                    trigger={"event": trigger_text, "evidence": refs},
                    timing_value=_clock(local, refs, anchor="termination or triggering event"),
                    amount_value=_money_after(local, fee_name, refs),
                    evidence=refs,
                    statement_id=stable_id("stmt", key),
                ))
    return results


def _context_unresolved(bundle):
    items = []
    for row in bundle.get("unresolved", []):
        related = [evidence_ref(source["source_id"]) for source in bundle.get("sources", [])
                   if source.get("section_id") == row.get("from_section_id")]
        items.append(unresolved(
            row.get("reason", "retrieval_dependency"),
            row.get("expression") or json.dumps(row.get("target", {}), sort_keys=True),
            dependency_id=row.get("from_section_id"), materiality="unknown",
            evidence=related,
        ))
    if bundle.get("budget", {}).get("truncated") and not items:
        items.append(unresolved("retrieval_budget_exhausted", "context bundle",
                                materiality="unknown"))
    return items
