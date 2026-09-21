import unittest
from unittest.mock import patch
from jev_investigator.providers import Qwen
from jev_investigator.engine import parsed_report
import json

class ProviderContractTests(unittest.TestCase):
    def choice_fixture(self, values=(0.49, 0.48, 0.02)):
        probabilities = {'c%02d' % i: v for i, v in enumerate(values)}
        model_input = {'state': {'text': 'bounded candidate state'}, 'question': {
            'type': 'choice', 'instructions': 'Choose next action',
            'criteria': {k: k for k in probabilities}}}
        raw = {'model': 'jev-1.13.0', 'usage': {}, 'answers': {'q': {
            'type': 'choice', 'choice': 'c00', 'confidence': 0.27, 'probabilities': probabilities}}}
        return model_input, raw

    def test_rounding_both_directions_leaves_benchmark_parser_strict(self):
        import copy
        from jev_bench.core import ValidationError, parse_response
        from jev_investigator.providers import parse_decision
        for values in ((0.49, 0.48, 0.02), (0.34, 0.34, 0.33)):
            with self.subTest(values=values):
                model_input, raw = self.choice_fixture(values)
                original = copy.deepcopy(raw)
                with self.assertRaisesRegex(ValidationError, '^probability_sum$'):
                    parse_response(model_input, raw)
                parsed, event = parse_decision(model_input, raw)
                self.assertEqual(raw, original)
                self.assertEqual(parsed['predicted'], 'c00')
                self.assertEqual(parsed['provider_confidence'], 0.27)
                self.assertAlmostEqual(sum(parsed['probabilities'].values()), 1.0)
                assert event is not None
                self.assertEqual(event['method'], 'cent-rounding-v1')
        model_input, raw = self.choice_fixture((0.5, 0.3, 0.2))
        self.assertIsNone(parse_decision(model_input, raw)[1])

    def test_rejects_excess_mass_non_cent_values_and_large_per_value_correction(self):
        from jev_bench.core import ValidationError
        from jev_investigator.providers import parse_decision
        for values in ((0.49, 0.47, 0.02), (0.49, 0.49, 0.04),
                       (0.491, 0.479, 0.02), (0.5, 0.49, 0.0), (0.99, 0.0, 0.0), (0.0, 0.0, 0.0)):
            with self.subTest(values=values):
                with self.assertRaisesRegex(ValidationError, '^probability_sum$'):
                    parse_decision(*self.choice_fixture(values))

    def test_rounding_never_admits_invalid_probabilities_confidence_or_selectors(self):
        from jev_bench.core import ValidationError
        from jev_investigator.providers import parse_decision
        for value in (-0.01, 1.01, True, '0.49', None, float('inf'), float('nan')):
            for field in ('probabilities', 'confidence'):
                with self.subTest(value=value, field=field):
                    model_input, raw = self.choice_fixture()
                    a = raw['answers']['q']
                    if field == 'probabilities': a[field]['c00'] = value
                    else: a[field] = value
                    with self.assertRaisesRegex(ValidationError, '^invalid_number$'):
                        parse_decision(model_input, raw)
        for choice in ('missing', 'c01', None, True):
            with self.subTest(choice=choice):
                model_input, raw = self.choice_fixture()
                raw['answers']['q']['choice'] = choice
                with self.assertRaisesRegex(ValidationError, '^choice_inconsistent$'):
                    parse_decision(model_input, raw)
        for operation in ('missing', 'extra'):
            model_input, raw = self.choice_fixture()
            p = raw['answers']['q']['probabilities']
            if operation == 'missing': del p['c02']
            else: p['unknown'] = 0.0
            with self.assertRaisesRegex(ValidationError, '^invalid_data$'):
                parse_decision(model_input, raw)

    def test_final_report_cites_tool_observations_not_prior_model_text(self):
        with patch('jev_investigator.providers.bounded_request', return_value={'status':'timeout'}) as request:
            Qwen().reason('final report',[{'id':'issue'},{'id':'commit'},{'id':'o0'},{'id':'report0'}],10)
        payload=request.call_args.args[0]
        citation=payload['format']['properties']['claims']['items']['properties']['citations']['items']
        self.assertEqual(citation['enum'],['o0'])

    def test_citations_constrained_to_supplied_ids_without_relaxing_validation(self):
        with patch('jev_investigator.providers.bounded_request', return_value={'status':'timeout'}) as request:
            Qwen().reason('hypothesis',[{'id':'issue'},{'id':'commit'}],10)
        payload=request.call_args.args[0]
        self.assertIsInstance(payload['format'],dict)
        citation=payload['format']['properties']['claims']['items']['properties']['citations']['items']
        self.assertEqual(citation['enum'],['issue','commit'])
        bad={'summary':'A hypothesis','claims':[{'text':'Inspect it','citations':['issue#1']}],'limitations':[]}
        with self.assertRaisesRegex(ValueError,'qwen_citation_invalid'):
            parsed_report({'status':'ok','model':'qwen2.5:7b','text':json.dumps(bad)},{'issue','commit'})
