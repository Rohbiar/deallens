import unittest
from deallens.quality import flag_candidates

class QualityTests(unittest.TestCase):
    def record(self,summary):
        return {'extraction_method':'llm','field_name':'remedy_limitations','candidate_value':{'summary':summary},'normalized_value':None,'review_status':'exception','status':'requires_review'}

    def test_flags_preserve_unverified_candidate(self):
        r=self.record('Remedies cannot materially adversely affect the parties.')
        flag_candidates([r])
        self.assertEqual(r['quality_flags'][0]['code'],'check_remedy_modality')
        self.assertIsNone(r['normalized_value'])
        self.assertEqual(r['review_status'],'exception')
        self.assertEqual(r['status'],'requires_review')

    def test_wrong_field_and_correct_no_duty_distinguished(self):
        wrong=self.record('The no-shop provision limits solicitation of competing offers.')
        correct=self.record('Parent is not required to accept a materially adverse divestiture.')
        flag_candidates([wrong,correct])
        self.assertEqual(wrong['quality_flags'][0]['code'],'possible_wrong_field')
        self.assertEqual(correct['quality_flags'],[])
