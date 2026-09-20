"""Conservative identity extraction from operative party introductions.

No issuer-based fallback and no transaction-specific names. Source spelling is
preserved. Covered-party declarations do not imply a complete guarantee scope.
"""
import re

ROLES = {'Company':'target', 'Target':'target', 'Parent':'parent_or_bidder',
         'Bidder':'parent_or_bidder', 'Acquiror':'parent_or_bidder',
         'Merger Sub':'acquisition_vehicle'}


def party_declarations(text):
    """Yield field, span, legal name, alias only within a recognizable introduction."""
    us = re.search(r'(?:made|entered into) by and among\s+', text[:1800], re.I)
    if us and re.search(r'AGREEMENT AND PLAN OF MERGER', text[:300], re.I):
        end = re.search(r'\bRECITALS\b|Certain capitalized terms|The Company, Parent', text[us.end():], re.I)
        stop = us.end()+end.start() if end else min(len(text), us.end()+2500)
        section = text[us.end():stop]
        # Entity descriptor terminates the name, allowing commas within a name.
        pattern = r'(?:^|(?<=\))\s*,?\s*(?:and\s+)?)(?P<name>[^()]+?),\s+(?:a|an)\s+[^()]{2,260}\((?:the\s+)?[“"](?P<alias>Company|Target|Parent|Bidder|Acquiror|Merger Sub)[”"]\)'
        for m in re.finditer(pattern, section):
            name = m.group('name').strip()
            # Do not accidentally treat a scope qualifier as part of an identity.
            if len(name)>160 or re.search(r'solely|purposes|provisions', name, re.I):
                continue
            yield ROLES[m.group('alias')], us.end()+m.start('name'), us.end()+m.end(), name, m.group('alias')
    elif re.match(r'PARTIES\s*\(1\)', text):
        stop = re.search(r'\bPREAMBLE\b', text)
        if not stop:
            return
        section = text[:stop.start()]
        # Numbered party blocks can contain nested parentheses and addresses.
        for block in re.finditer(r'\(\d+\)\s*(.*?)(?=\(\d+\)|$)', section):
            body=block.group(1)
            name=re.match(r'(.+?),\s+(?:a|an)\s+', body)
            alias=re.search(r'\(the (Bidder|Company|Target|Acquiror)(?:\s+or\s+[^)]*)?\)', body)
            if name and alias:
                start=block.start(1)
                field=ROLES[alias.group(1)]
                yield field,start,start+alias.end(),name.group(1),alias.group(1)
                if alias.group(1)=='Bidder':
                    yield 'acquisition_vehicle',start,start+alias.end(),name.group(1),alias.group(1)
