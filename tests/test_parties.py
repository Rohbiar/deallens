import unittest
from deallens.parties import party_declarations
from deallens.extract import scalar_matches

class PartyTests(unittest.TestCase):
    def test_adjacent_definitions_and_commas_in_legal_names(self):
        text = 'AGREEMENT AND PLAN OF MERGER is made by and among Example Parent, Inc., a Delaware corporation (“Parent”), Example Sub, Inc., a Delaware corporation (“Merger Sub”), and Example Target & Co., a Minnesota corporation (the “Company”). RECITALS'
        result = {r[0]:r[3] for r in party_declarations(text)}
        self.assertEqual(result, {'parent_or_bidder':'Example Parent, Inc.', 'acquisition_vehicle':'Example Sub, Inc.', 'target':'Example Target & Co.'})

    def test_alias_without_operative_intro_does_not_resolve_identity(self):
        text = 'The Parent shall perform its obligations. Example Bank, a Delaware corporation (the “Company”).'
        self.assertEqual(list(scalar_matches('target',text)), [])

    def test_numbered_foreign_party_preserves_bidder_and_nested_parentheses(self):
        text = 'PARTIES (1) TEST BIDDER CORPORATION, a corporation registered under number 123 (the Bidder); and (2) TEST TARGET SE, a European Company (Societas Europaea), registered with the register (Handelsregister) under number 987 (the Company or Target), PREAMBLE'
        result={r[0]:r[3] for r in party_declarations(text)}
        self.assertEqual(result['target'],'TEST TARGET SE')
        self.assertEqual(result['acquisition_vehicle'],'TEST BIDDER CORPORATION')
