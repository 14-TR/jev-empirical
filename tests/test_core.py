import copy
import importlib
import json
import unittest


def core_module(test):
    try:
        return importlib.import_module("jev_bench.core")
    except ImportError:
        test.fail("dataset loading and label-blind model input are not implemented")


def fixture():
    return {"schema_version": 1, "provenance": "original-authored-synthetic-diagnostic",
            "name": "tiny", "cases": [
        {"id": "route-1", "task": "routing", "pair_id": "route-1", "variant": "base",
         "input": {"state": {"text": "Please refund this charge."},
                   "question": {"type": "choice", "instructions": "Pick a support team.",
                                "criteria": {"billing": "Payments", "technical": "Bugs"}}},
         "gold": "billing"}]}


class DatasetTests(unittest.TestCase):
    def test_dataset_to_request_never_serializes_gold(self):
        c = core_module(self)
        dataset = c.validate_dataset(fixture())
        case = dataset["cases"][0]
        request = c.request_for(case["input"], "jev-1.13.0")
        self.assertEqual(set(request), {"state", "model", "questions"})
        self.assertEqual(request["questions"], {"q": case["input"]["question"]})
        changed = copy.deepcopy(case)
        changed["gold"] = "technical"
        self.assertEqual(request, c.request_for(changed["input"], "jev-1.13.0"))
        self.assertNotIn("gold", json.dumps(request))
        with self.assertRaises(c.ValidationError):
            c.request_for(case, "jev-1.13.0")

    def test_empty_missing_duplicate_and_unknown_data_fail_closed(self):
        c = core_module(self)
        invalid = [None, {}, {**fixture(), "cases": []}]
        for field in ("id", "gold", "input", "task", "pair_id", "variant"):
            d = fixture(); del d["cases"][0][field]; invalid.append(d)
        d = fixture(); d["cases"] *= 2; invalid.append(d)
        d = fixture(); d["cases"][0]["input"]["gold"] = "billing"; invalid.append(d)
        d = fixture(); d["cases"][0]["gold"] = "not-an-option"; invalid.append(d)
        d = fixture(); d["cases"][0]["variant"] = "paraphrase"; invalid.append(d)
        for d in invalid:
            with self.subTest(d=d), self.assertRaises(c.ValidationError):
                c.validate_dataset(d)
        for raw in ('{}', '{"x":1,"x":2}', '{"x":NaN}', ''):
            with self.subTest(raw=raw), self.assertRaises(c.ValidationError):
                c.validate_dataset(c.strict_json(raw))
