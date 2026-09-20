"""Descriptive metrics; correlated synthetic cases are not IID samples."""
import math
from collections import Counter
from .core import require


def mean(values):
    return sum(values) / len(values) if values else None


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    position = (len(values) - 1) * q
    lo, hi = math.floor(position), math.ceil(position)
    return values[lo] + (values[hi] - values[lo]) * (position - lo)


def correct(row):
    return row["prediction"]["predicted"] == row["case"]["gold"]


def top_probability(row):
    return max(row["prediction"]["probabilities"].values())


def summarize(rows):
    require(bool(rows), "empty_metrics")
    good = [r for r in rows if r["status"] == "ok"]
    brier, losses, ordinal = [], [], []
    for r in good:
        p, gold = r["prediction"], r["case"]["gold"]
        brier.append(sum((v - int(k == gold)) ** 2 for k, v in p["probabilities"].items()))
        losses.append(-math.log(max(p["probabilities"][gold], 1e-15)))
        if p["expected_score"] is not None:
            ordinal.append(abs(p["expected_score"] - int(gold)))
    bins = []
    for i in range(10):
        members = [r for r in good if min(int(top_probability(r) * 10), 9) == i]
        bins.append({"lower": i / 10, "upper": (i + 1) / 10, "n": len(members),
                     "mean_probability": mean([top_probability(r) for r in members]),
                     "accuracy": mean([int(correct(r)) for r in members])})
    curve = []
    for threshold in sorted({top_probability(r) for r in good}, reverse=True):
        members = [r for r in good if top_probability(r) >= threshold]
        curve.append({"threshold_top_probability": threshold, "n_accepted": len(members),
                      "coverage_all_cases": len(members) / len(rows),
                      "coverage_success_only": len(members) / len(good),
                      "risk": 1 - sum(correct(r) for r in members) / len(members)})
    latencies = [r["latency_ms"] for r in rows if r["latency_ms"] is not None]
    return {"n_cases": len(rows), "n_success": len(good), "n_failed": len(rows) - len(good),
            "failure_counts": dict(sorted(Counter(r["status"] for r in rows if r["status"] != "ok").items())),
            "accuracy_success_only": mean([int(correct(r)) for r in good]),
            "accuracy_all_cases": sum(correct(r) for r in good) / len(rows),
            "brier_multiclass": mean(brier), "log_loss": mean(losses),
            "ordinal_expected_score_mae": mean(ordinal), "n_ordinal_success": len(ordinal),
            "mean_provider_confidence": mean([r["prediction"]["provider_confidence"] for r in good
                                               if r["prediction"]["provider_confidence"] is not None]),
            "calibration_top_probability": bins, "risk_coverage": curve,
            "latency_ms_attempted": {"n": len(latencies),
                **{name: percentile(latencies, q) for name, q in (("p50", .5), ("p95", .95), ("p99", .99))}}}


def robustness(rows):
    bases = {r["case"]["pair_id"]: r for r in rows if r["case"]["variant"] == "base"}
    families = {}
    for r in rows:
        if r["case"]["variant"] != "base":
            families.setdefault(r["case"]["variant"], []).append((bases[r["case"]["pair_id"]], r))
    result = {}
    for family, pairs in sorted(families.items()):
        complete = [(a, b) for a, b in pairs if a["status"] == b["status"] == "ok"]
        result[family] = {
            "n_pairs": len(pairs), "n_complete_pairs": len(complete),
            "accuracy_delta_variant_minus_base": mean([int(correct(b)) - int(correct(a)) for a, b in complete]),
            "accuracy_delta_all_pairs_failures_incorrect": mean([
                int(b["status"] == "ok" and correct(b)) - int(a["status"] == "ok" and correct(a)) for a, b in pairs]),
            "prediction_flip_rate": mean([int(a["prediction"]["predicted"] != b["prediction"]["predicted"])
                                           for a, b in complete]),
            "mean_total_variation": mean([sum(abs(a["prediction"]["probabilities"][k] - v)
                                               for k, v in b["prediction"]["probabilities"].items()) / 2
                                           for a, b in complete])}
    return result
