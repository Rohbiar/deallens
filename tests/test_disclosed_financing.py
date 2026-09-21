import unittest
from deallens.financing import disclosed_pricing
from test_provisions import document


class DisclosedFinancingTests(unittest.TestCase):
    def fixture(self):
        return document(['1.01 Defined Terms.\n“Applicable Rate” means percentages per annum: EURIBOR Loans Pricing Level Debt Rating Commitment Fee and ESTR Loans 1 A/A2/A 0.06% 0.625% 2 BBB/Baa2/BBB 0.10% 1.00% The rate is increased by an additional [****] on the 90th day.\n“Other Term” means other terms.\n2.09 Fees.\nA duration fee equal to [****] and a funding fee for each Lender equal to [****] are payable.\n2.10 Other.\nOther terms.'],['financing-agreement'])

    def test_public_grid_and_redactions_remain_separate(self):
        r=disclosed_pricing(self.fixture())
        self.assertEqual(r['status'],'disclosed_grid')
        self.assertEqual(r['pricing_grid'][0]['loan_margin_rate'],.00625)
        self.assertEqual(r['pricing_grid'][1]['commitment_fee_rate'],.001)
        self.assertEqual(set(r['redacted_components']),{'margin_stepup_amount','duration_fee_amount','funding_fee_amount'})

    def test_different_column_order_blocks_normalization(self):
        d=self.fixture()
        for key in ['raw_text','text']:
            d['pages'][0][key]=d['pages'][0][key].replace('Commitment Fee and ESTR Loans','ESTR Loans and Commitment Fee')
        self.assertEqual(disclosed_pricing(d)['status'],'unresolved_table_layout')

    def test_missing_pricing_level_blocks_partial_table(self):
        d=self.fixture()
        for key in ['raw_text','text']:
            d['pages'][0][key]=d['pages'][0][key].replace('2 BBB','3 BBB')
        self.assertEqual(disclosed_pricing(d)['pricing_grid'],[])
