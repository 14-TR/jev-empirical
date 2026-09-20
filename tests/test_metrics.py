import importlib
import math
import unittest
from test_core import fixture
from jev_bench.core import uniform_baseline


class MetricsTests(unittest.TestCase):
    def api(self):
        try: return importlib.import_module("jev_bench.metrics")
        except ImportError: self.fail("metrics missing")

    def test_hand_checked_classification_failures_and_calibration(self):
        m = self.api()
        c = fixture()["cases"][0]
        p = {"probabilities": {"billing": 0.8, "technical": 0.2}, "predicted": "billing",
             "provider_confidence": 0.7, "expected_score": None}
        other = dict(c, id="second", gold="technical")
        rows = [{"case": c, "prediction": p, "status": "ok", "latency_ms": 10},
                {"case": other, "prediction": p, "status": "ok", "latency_ms": 30},
                {"case": c, "prediction": None, "status": "timeout", "latency_ms": 20}]
        out = m.summarize(rows)
        self.assertEqual(out["n_cases"], 3)
        self.assertEqual(out["n_success"], 2)
        self.assertEqual(out["accuracy_success_only"], 0.5)
        self.assertAlmostEqual(out["accuracy_all_cases"], 1/3)
        self.assertAlmostEqual(out["brier_multiclass"], 0.68)
        self.assertAlmostEqual(out["log_loss"], -math.log(0.16)/2)
        self.assertEqual(out["latency_ms_attempted"]["p50"], 20)
        self.assertEqual(out["latency_ms_attempted"]["p95"], 29)
        self.assertEqual(sum(b["n"] for b in out["calibration_top_probability"]), 2)
        self.assertAlmostEqual(out["risk_coverage"][0]["coverage_all_cases"], 2/3)
        self.assertEqual(out["risk_coverage"][0]["risk"], 0.5)
        self.assertEqual(len(out["risk_coverage"]), 1)  # ties enter together
        self.assertNotEqual(out["calibration_top_probability"][-2]["mean_probability"], 0.7)

    def test_empty_rejected_all_failure_described_not_divided_by_zero(self):
        m = self.api()
        with self.assertRaises(ValueError): m.summarize([])
        out = m.summarize([{"case": fixture()["cases"][0], "status": "budget_exhausted",
                            "prediction": None, "latency_ms": None}])
        self.assertIsNone(out["accuracy_success_only"])
        self.assertEqual(out["accuracy_all_cases"], 0)
        self.assertIsNone(out["latency_ms_attempted"]["p50"])

    def test_paired_deltas_and_ordinal_mae(self):
        m = self.api()
        base = fixture()["cases"][0]
        perturbed = dict(base, id="route-1-paraphrase", variant="paraphrase")
        p1 = {"probabilities": {"billing": 1., "technical": 0.}, "predicted": "billing",
              "provider_confidence": 1., "expected_score": None}
        p2 = {"probabilities": {"billing": 0., "technical": 1.}, "predicted": "technical",
              "provider_confidence": 1., "expected_score": None}
        rows = [{"case": c, "prediction": p, "status": "ok", "latency_ms": 1}
                for c, p in [(base,p1),(perturbed,p2)]]
        pair = m.robustness(rows)["paraphrase"]
        self.assertEqual(pair["n_complete_pairs"], 1)
        self.assertEqual(pair["accuracy_delta_variant_minus_base"], -1)
        self.assertEqual(pair["mean_total_variation"], 1)
        self.assertEqual(pair["prediction_flip_rate"], 1)
        from test_answers import input_for
        c = dict(base, input=input_for("score"), gold="2")
        out = m.summarize([{"case": c, "prediction": uniform_baseline(c["input"]),
                            "status": "ok", "latency_ms": 0}])
        self.assertEqual(out["ordinal_expected_score_mae"], 1.)
