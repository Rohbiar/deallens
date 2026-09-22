"""Bounded, source-faithful dependency expansion for provision retrieval.

The bundle is deliberately an evidence graph, not a legal interpretation.  Text
only appears in exact page spans already produced by :mod:`deallens.provisions`.
"""
from __future__ import annotations

import hashlib
import re


SCHEMA_VERSION = "retrieval-context/v1"

# Capture the useful local grammar rather than pretending every legal reference
# style is understood.  The recognition report preserves expressions we cannot
# parse so callers cannot equate resolved known references with completeness.
REFERENCE_EXPRESSION = re.compile(
    r"\b(?:Sections?|Clauses?)\s+\d{1,2}\.\d{1,2}(?:\([A-Za-z0-9]+\))*"
    r"(?:\s*(?:,\s*(?:and|or)?|and|or)\s*(?:(?:Sections?|Clauses?)\s+)?"
    r"(?:\d{1,2}\.\d{1,2}(?:\([A-Za-z0-9]+\))*|\([A-Za-z0-9]+\)))*\s*",
    re.I,
)
# Capitalization filters ordinary internal phrases such as "clause (a) below";
# those subclauses are already retained inside their complete parent section.
REFERENCE_MENTION = re.compile(
    r"\b(?:Sections?|Clauses?)\b(?:(?![;:\n]|\.\s+[A-Z]).){0,120}"
)
EXPLICIT_TARGET = re.compile(r"(\d{1,2}\.\d{1,2})((?:\([A-Za-z0-9]+\))*)")
BARE_SUBSECTION = re.compile(r"(?:(?<=,)|(?<=and)|(?<=or))\s*(\([A-Za-z0-9]+\))", re.I)
SCHEDULE_REFERENCE = re.compile(
    r"\b(?:Schedule|Annex|Exhibit)\s+[A-Z0-9][A-Z0-9.\-]*(?:\s+to\s+this\s+Agreement)?",
    re.I,
)
QUOTED_TERM = re.compile(r"[\u201c\"]([^\u201d\"\n]{2,100})[\u201d\"]")


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}:{hashlib.sha256(value.encode()).hexdigest()[:20]}"


def _target_groups(expression: str):
    """Return section targets with all expressly grouped subsections."""
    groups = []
    matches = list(EXPLICIT_TARGET.finditer(expression))
    for i, match in enumerate(matches):
        subsections = re.findall(r"\(([A-Za-z0-9]+)\)", match.group(2))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(expression)
        tail = expression[match.end():end]
        subsections.extend(x.strip("()") for x in BARE_SUBSECTION.findall(tail))
        groups.append((match.group(1), subsections))
    return groups


def _reference_expressions(text: str):
    parsed = [(m.span(), m.group().strip()) for m in REFERENCE_EXPRESSION.finditer(text)]
    unrecognized = []
    for mention in REFERENCE_MENTION.finditer(text):
        overlaps = [expression for (a, b), expression in parsed
                    if not (b <= mention.start() or a >= mention.end())]
        mentioned_targets = [m.group() for m in EXPLICIT_TARGET.finditer(mention.group())]
        parsed_targets = [m.group() for expression in overlaps
                          for m in EXPLICIT_TARGET.finditer(expression)]
        if not overlaps or mentioned_targets != parsed_targets:
            unrecognized.append(mention.group().strip())
    return parsed, unrecognized


def _definition_index(sections):
    index = {}
    for section in sections:
        if not re.search(r"Definitions|Defined Terms", section["title"], re.I):
            continue
        starts = list(re.finditer(
            r"[\u201c\"]([^\u201d\"\n]{2,100})[\u201d\"]\s+(?:means|has the meaning)",
            section["text"], re.I,
        ))
        for position, match in enumerate(starts):
            end = starts[position + 1].start() if position + 1 < len(starts) else len(section["text"])
            index.setdefault((section["layer"], match.group(1)), []).append(
                (section, match.start(), end)
            )
    return index


def build_context_bundle(
    doc,
    sections,
    selected_sections,
    *,
    definition_terms=(),
    max_depth=3,
    max_chars=60_000,
    max_nodes=64,
):
    """Build a JSON-safe recursive context graph in source order.

    Expansion never crosses an instrument boundary.  Roots are always retained;
    budgets bound additional section/definition dependencies.
    """
    lookup = {}
    for section in sections:
        lookup.setdefault((section["layer"], section["number"]), []).append(section)
    definition_index = _definition_index(sections)

    bundle = {
        "schema_version": SCHEMA_VERSION,
        "source_hash": doc["sha256"],
        "document_id": doc["document_id"],
        "root_section_ids": [s["section_id"] for s in selected_sections],
        "section_ids": [],
        "sections": [],
        "definitions": [],
        "sources": [],
        "edges": [],
        "unresolved": [],
        "budget": {
            "max_depth": max_depth, "max_chars": max_chars, "max_nodes": max_nodes,
            "used_chars": 0, "used_nodes": 0, "truncated": False,
            "exhausted_by": [],
        },
        "recognition": {
            "reference_expressions": 0, "recognized_targets": 0,
            "unrecognized_expressions": [],
        },
        "completeness": "not_established",
    }
    source_ids = set()
    section_ids = set()
    definition_ids = set()
    definition_sources = {}

    def add_unresolved(kind, from_id, expression, target, reason, details=None):
        row = {"kind": kind, "from_section_id": from_id, "expression": expression,
               "target": target, "reason": reason, "details": details}
        bundle["unresolved"].append(row)

    def exhaust(reason):
        budget = bundle["budget"]
        budget["truncated"] = True
        if reason not in budget["exhausted_by"]:
            budget["exhausted_by"].append(reason)

    def can_add(chars):
        budget = bundle["budget"]
        if budget["used_nodes"] >= max_nodes:
            return "node_budget"
        if budget["used_chars"] + chars > max_chars:
            return "character_budget"
        return None

    def add_sources(spans):
        ids = []
        for span in spans:
            ids.append(span["source_id"])
            if span["source_id"] not in source_ids:
                bundle["sources"].append(dict(span))
                source_ids.add(span["source_id"])
        return ids

    def add_section(section, root=False, force=False):
        if section["section_id"] in section_ids:
            return None
        reason = None if force else can_add(len(section["text"]))
        if reason:
            exhaust(reason)
            return reason
        ids = add_sources(section["sources"])
        bundle["sections"].append({
            "section_id": section["section_id"], "document_layer": section["layer"],
            "number": section["number"], "title": section["title"], "root": root,
            "source_ids": ids, "boundary": section["boundary"],
        })
        bundle["section_ids"].append(section["section_id"])
        section_ids.add(section["section_id"])
        bundle["budget"]["used_chars"] += len(section["text"])
        bundle["budget"]["used_nodes"] += 1
        if force and (bundle["budget"]["used_chars"] > max_chars or bundle["budget"]["used_nodes"] > max_nodes):
            exhaust("root_exceeds_budget")
        return None

    for section in selected_sections:
        add_section(section, root=True, force=True)

    queue = [(s, (s["section_id"],), 0) for s in selected_sections]
    expanded = set()
    while queue:
        section, ancestry, depth = queue.pop(0)
        state = (section["section_id"], depth)
        if state in expanded:
            continue
        expanded.add(state)
        parsed, unrecognized = _reference_expressions(section["text"])
        bundle["recognition"]["reference_expressions"] += len(parsed)
        for expression in unrecognized:
            if expression not in bundle["recognition"]["unrecognized_expressions"]:
                bundle["recognition"]["unrecognized_expressions"].append(expression)
            add_unresolved("reference", section["section_id"], expression, {},
                           "unrecognized_reference")
        for _, expression in parsed:
            for number, subsections in _target_groups(expression):
                bundle["recognition"]["recognized_targets"] += 1
                target_spec = {"document_layer": section["layer"], "section_number": number,
                               "subsections": subsections}
                targets = lookup.get((section["layer"], number), [])
                # A section heading and internal subsection pointers are already
                # contained in the current node; they are not dependencies.
                if len(targets) == 1 and targets[0]["section_id"] == section["section_id"]:
                    continue
                edge = {"kind": "reference", "from_section_id": section["section_id"],
                        "to_section_id": None, "expression": expression,
                        "target": target_spec, "status": None, "reason": None,
                        "source_ids": []}
                if not targets:
                    other_layers = sorted({s["layer"] for s in sections if s["number"] == number})
                    reason = "instrument_boundary" if other_layers else "missing_target"
                    edge.update(status="missing", reason=reason)
                    add_unresolved("reference", section["section_id"], expression,
                                   target_spec, reason, {"other_layers": other_layers})
                elif len(targets) > 1:
                    edge.update(status="ambiguous", reason="ambiguous_target")
                    add_unresolved("reference", section["section_id"], expression,
                                   target_spec, "ambiguous_target",
                                   {"candidate_section_ids": [t["section_id"] for t in targets]})
                else:
                    target = targets[0]
                    edge["to_section_id"] = target["section_id"]
                    if target["section_id"] in ancestry:
                        edge.update(status="cycle", reason="cycle_detected")
                        add_unresolved("reference", section["section_id"], expression,
                                       target_spec, "cycle_detected")
                    elif depth >= max_depth:
                        edge.update(status="depth_limit", reason="depth_limit")
                        exhaust("depth_limit")
                        add_unresolved("reference", section["section_id"], expression,
                                       target_spec, "depth_limit")
                    else:
                        reason = add_section(target)
                        if reason:
                            edge.update(status="budget_exhausted", reason=reason)
                            add_unresolved("reference", section["section_id"], expression,
                                           target_spec, reason)
                        else:
                            edge.update(status="resolved", source_ids=[s["source_id"] for s in target["sources"]])
                            queue.append((target, ancestry + (target["section_id"],), depth + 1))
                bundle["edges"].append(edge)

        for match in SCHEDULE_REFERENCE.finditer(section["text"]):
            expression = match.group()
            target_spec = {"document_layer": section["layer"], "schedule": expression}
            edge = {"kind": "reference", "from_section_id": section["section_id"],
                    "to_section_id": None, "expression": expression, "target": target_spec,
                    "status": "missing", "reason": "missing_target", "source_ids": []}
            bundle["edges"].append(edge)
            add_unresolved("reference", section["section_id"], expression, target_spec,
                           "missing_target", "Schedules/annexes are not indexed as numbered sections.")

    roots_by_layer = {}
    for section in selected_sections:
        roots_by_layer.setdefault(section["layer"], section["section_id"])
    definition_queue = [
        (layer, term, root_id, 0, ())
        for layer, root_id in roots_by_layer.items()
        for term in definition_terms
    ]
    while definition_queue:
        layer, term, from_id, depth, ancestry = definition_queue.pop(0)
        definition_id = _stable_id("definition", f"{doc['sha256']}:{layer}:{term}")
        target_spec = {"document_layer": layer, "term": term}
        edge = {"kind": "definition", "from_section_id": from_id,
                "to_section_id": None, "expression": term, "target": target_spec,
                "status": None, "reason": None, "source_ids": []}
        found = definition_index.get((layer, term), [])
        if not found:
            edge.update(status="missing", reason="missing_definition")
            add_unresolved("definition", from_id, term, target_spec, "missing_definition")
        elif len(found) > 1:
            edge.update(status="ambiguous", reason="ambiguous_target")
            add_unresolved("definition", from_id, term, target_spec, "ambiguous_target")
        elif definition_id in ancestry:
            edge.update(status="cycle", reason="cycle_detected")
            add_unresolved("definition", from_id, term, target_spec, "cycle_detected")
        elif definition_id in definition_ids:
            edge.update(status="resolved", source_ids=definition_sources[definition_id])
        elif depth > max_depth:
            edge.update(status="depth_limit", reason="depth_limit")
            exhaust("depth_limit")
            add_unresolved("definition", from_id, term, target_spec, "depth_limit")
        else:
            section, start, end = found[0]
            spans = _slice_sources(section["sources"], start, end, definition_id)
            chars = sum(len(s["evidence"]) for s in spans)
            reason = can_add(chars)
            if reason:
                edge.update(status="budget_exhausted", reason=reason)
                exhaust(reason)
                add_unresolved("definition", from_id, term, target_spec, reason)
            else:
                ids = add_sources(spans)
                definition_ids.add(definition_id)
                definition_sources[definition_id] = ids
                bundle["definitions"].append({
                    "definition_id": definition_id, "document_layer": layer,
                    "term": term, "section_id": section["section_id"], "source_ids": ids,
                })
                bundle["budget"]["used_chars"] += chars
                bundle["budget"]["used_nodes"] += 1
                edge.update(status="resolved", source_ids=ids)
                definition_text = " ".join(s["evidence"] for s in spans)
                for nested in QUOTED_TERM.findall(definition_text):
                    if nested != term and (layer, nested) in definition_index:
                        definition_queue.append((layer, nested, section["section_id"], depth + 1,
                                                 ancestry + (definition_id,)))
        bundle["edges"].append(edge)

    return bundle


def _slice_sources(sources, start, end, definition_id):
    """Slice joined section text and give resulting definition spans stable IDs."""
    result = []
    cursor = 0
    for source in sources:
        length = len(source["evidence"])
        a, b = max(0, start - cursor), min(length, end - cursor)
        if b > a:
            span = dict(source)
            span.update(start=source["start"] + a, end=source["start"] + b,
                        evidence=source["evidence"][a:b], definition_id=definition_id)
            span["locator"] = source["locator"].split(":chars")[0] + f":chars{span['start']}-{span['end']}"
            span["source_id"] = _stable_id(
                "source", f"{span['document_sha256']}:{span['locator']}:{definition_id}"
            )
            result.append(span)
        cursor += length + 1
    return result
