import copy
import math
import unittest
from test_core import core_module, fixture


def response(kind="choice"):
    # Authored test fixture only. Never an empirical/model receipt.
    answer = {"type": "choice", "choice": "billing", "confidence": 0.7,
              "probabilities": {"billing": 0.8, "technical": 0.2}}
    if kind == "noul":
        answer = {"type": "noul", "noul": 0.7}
    if kind == "score":
        answer = {"type": "score", "score": 1.3, "confidence": 0.54,
                  "probabilities": {"0": 0.0, "1": 0.7, "2": 0.3},
                  "legend": {"0": "Cosmetic", "1": "Workaround", "2": "Blocked"}}
    return {"model": "jev-1.13.0", "answers": {"q": answer},
            "usage": {"input_tokens": 10, "output_tokens": 2}}


def input_for(kind):
    inp = fixture()["cases"][0]["input"]
    if kind == "noul":
        inp["question"] = {"type": kind, "instructions": "Is it urgent?",
                           "criteria": {"true": "Urgent", "false": "Not urgent"}}
    if kind == "score":
        inp["question"] = {"type": kind, "instructions": "Rate severity.",
                           "criteria": ["Cosmetic", "Workaround", "Blocked"]}
    return inp


class AnswerTests(unittest.TestCase):
    def api(self):
        c = core_module(self)
        self.assertTrue(hasattr(c, "parse_response"), "strict API response decoder missing")
        return c

    def test_all_three_documented_answer_types(self):
        c = self.api()
        choice = c.parse_response(input_for("choice"), response())
        self.assertEqual(choice["predicted"], "billing")
        noul = c.parse_response(input_for("noul"), response("noul"))
        self.assertAlmostEqual(noul["probabilities"]["false"], 0.3)
        self.assertEqual(noul["probabilities"]["true"], 0.7)
        self.assertIsNone(noul["provider_confidence"])
        score = c.parse_response(input_for("score"), response("score"))
        self.assertAlmostEqual(score["expected_score"], 1.3)
        self.assertEqual(score["predicted"], "1")
        self.assertEqual(score["provider_confidence"], 0.54)

    def test_malformed_probabilities_missing_answers_and_inconsistency_rejected(self):
        c = self.api()
        bad = [None, {}, {**response(), "answers": {}}, {**response(), "model": "evil\nmodel"}]
        for p in ({"billing": 0.5}, {"billing": 0.8, "technical": 0.8},
                  {"billing": -0.1, "technical": 1.1}, {"billing": True, "technical": 0.0},
                  {"billing": math.nan, "technical": 0.0}, {"billing": 1, "technical": 0, "extra": 0}):
            r = response(); r["answers"]["q"]["probabilities"] = p; bad.append(r)
        r = response(); r["answers"]["q"]["choice"] = "technical"; bad.append(r)
        r = response(); del r["answers"]["q"]["confidence"]; bad.append(r)
        for r in bad:
            with self.subTest(r=r), self.assertRaises(c.ValidationError):
                c.parse_response(input_for("choice"), r)
        r = response("score"); r["answers"]["q"]["score"] = 0.1
        with self.assertRaises(c.ValidationError): c.parse_response(input_for("score"), r)
        r = response("noul"); r["answers"]["q"]["noul"] = 2
        with self.assertRaises(c.ValidationError): c.parse_response(input_for("noul"), r)

    def test_uniform_baseline_has_no_provider_claim_and_is_label_blind(self):
        c = self.api()
        self.assertTrue(hasattr(c, "uniform_baseline"))
        p = c.uniform_baseline(input_for("choice"))
        self.assertEqual(p["probabilities"], {"billing": 0.5, "technical": 0.5})
        self.assertIsNone(p["provider_confidence"])
        self.assertEqual(c.uniform_baseline(input_for("score"))["expected_score"], 1)
