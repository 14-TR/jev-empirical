# Jev live diagnostic results

Dataset SHA-256: `a97b324fc1954b9f283eda409d6403d3479ff4c0d6d49fc8ec1728459c42d1de`

| Task | Cases | Success | Accuracy (all) | Brier (success) | Log loss (success) |
|---|---:|---:|---:|---:|---:|
| candidate | 24 | 24 | 1.000000 | 0.000100 | 0.003359 |
| evidence | 18 | 18 | 1.000000 | 0.000044 | 0.001122 |
| ordinal | 15 | 15 | 1.000000 | 0.000000 | 0.000000 |
| predicate | 20 | 20 | 1.000000 | 0.006010 | 0.041172 |
| routing | 24 | 24 | 1.000000 | 0.000300 | 0.002578 |

## Interpretation

- Original authored synthetic diagnostics; not a representative benchmark.
- Baseline is uniform probabilities, label-blind; not Jev outputs.
- Class prediction uses argmax; ties are class-order deterministic except provider Choice ties.
- Score MAE uses probability-weighted level index; Score accuracy uses modal level.
- Brier is sum over classes (binary included); log loss clips at 1e-15; both success-only.
- Calibration uses top-class probability, NOT provider confidence; ten fixed bins; final bin includes one.
- Risk coverage admits tied top probabilities together; failures never accepted.
- Latency percentiles use linear interpolation over attempted calls, including failed calls.
- Baseline latency is a zero placeholder, not a speed measurement.
- Paired families are correlated; no statistical significance or generalization claim.
- Receipts are local provenance records, not cryptographic provider attestations.
- Usage excludes failed calls; reported tokens are not a billing reconciliation.

## Complete sanitized metrics

```json
{
  "report_schema_version": 1,
  "harness_version": "0.1.0",
  "code_sha256": "4c224974295c03d75929b55698cee900910d8f907584377b0f744277f09468fb",
  "dataset_sha256": "a97b324fc1954b9f283eda409d6403d3479ff4c0d6d49fc8ec1728459c42d1de",
  "mode": "live",
  "requested_model": "jev-1.13.0",
  "resolved_models": [
    "jev-1.13.0"
  ],
  "dataset_provenance": "original-authored-synthetic-diagnostic",
  "summary": {
    "n_cases": 101,
    "n_success": 101,
    "n_failed": 0,
    "failure_counts": {},
    "accuracy_success_only": 1.0,
    "accuracy_all_cases": 1.0,
    "brier_multiclass": 0.0012930693069306935,
    "log_loss": 0.009763677797917512,
    "ordinal_expected_score_mae": 0.0,
    "n_ordinal_success": 15,
    "mean_provider_confidence": 0.997037037037037,
    "calibration_top_probability": [
      {
        "lower": 0.0,
        "upper": 0.1,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.1,
        "upper": 0.2,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.2,
        "upper": 0.3,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.3,
        "upper": 0.4,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.4,
        "upper": 0.5,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.5,
        "upper": 0.6,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.6,
        "upper": 0.7,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.7,
        "upper": 0.8,
        "n": 0,
        "mean_probability": null,
        "accuracy": null
      },
      {
        "lower": 0.8,
        "upper": 0.9,
        "n": 1,
        "mean_probability": 0.8,
        "accuracy": 1.0
      },
      {
        "lower": 0.9,
        "upper": 1.0,
        "n": 100,
        "mean_probability": 0.9924999999999998,
        "accuracy": 1.0
      }
    ],
    "risk_coverage": [
      {
        "threshold_top_probability": 1.0,
        "n_accepted": 73,
        "coverage_all_cases": 0.7227722772277227,
        "coverage_success_only": 0.7227722772277227,
        "risk": 0.0
      },
      {
        "threshold_top_probability": 0.99,
        "n_accepted": 77,
        "coverage_all_cases": 0.7623762376237624,
        "coverage_success_only": 0.7623762376237624,
        "risk": 0.0
      },
      {
        "threshold_top_probability": 0.98,
        "n_accepted": 87,
        "coverage_all_cases": 0.8613861386138614,
        "coverage_success_only": 0.8613861386138614,
        "risk": 0.0
      },
      {
        "threshold_top_probability": 0.97,
        "n_accepted": 91,
        "coverage_all_cases": 0.900990099009901,
        "coverage_success_only": 0.900990099009901,
        "risk": 0.0
      },
      {
        "threshold_top_probability": 0.96,
        "n_accepted": 98,
        "coverage_all_cases": 0.9702970297029703,
        "coverage_success_only": 0.9702970297029703,
        "risk": 0.0
      },
      {
        "threshold_top_probability": 0.95,
        "n_accepted": 99,
        "coverage_all_cases": 0.9801980198019802,
        "coverage_success_only": 0.9801980198019802,
        "risk": 0.0
      },
      {
        "threshold_top_probability": 0.94,
        "n_accepted": 100,
        "coverage_all_cases": 0.9900990099009901,
        "coverage_success_only": 0.9900990099009901,
        "risk": 0.0
      },
      {
        "threshold_top_probability": 0.8,
        "n_accepted": 101,
        "coverage_all_cases": 1.0,
        "coverage_success_only": 1.0,
        "risk": 0.0
      }
    ],
    "latency_ms_attempted": {
      "n": 101,
      "p50": 311.84266600000046,
      "p95": 382.480791,
      "p99": 434.6625420000016
    }
  },
  "by_task": {
    "candidate": {
      "n_cases": 24,
      "n_success": 24,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.00010000000000000009,
      "log_loss": 0.0033586149187101975,
      "ordinal_expected_score_mae": null,
      "n_ordinal_success": 0,
      "mean_provider_confidence": 0.9958333333333332,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 24,
          "mean_probability": 0.9966666666666667,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 18,
          "coverage_all_cases": 0.75,
          "coverage_success_only": 0.75,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.99,
          "n_accepted": 22,
          "coverage_all_cases": 0.9166666666666666,
          "coverage_success_only": 0.9166666666666666,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 24,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 24,
        "p50": 291.60193749999917,
        "p95": 369.52302140000035,
        "p99": 398.51725322999914
      }
    },
    "evidence": {
      "n_cases": 18,
      "n_success": 18,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 4.444444444444449e-05,
      "log_loss": 0.0011223726287510815,
      "ordinal_expected_score_mae": null,
      "n_ordinal_success": 0,
      "mean_provider_confidence": 0.9977777777777779,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 18,
          "mean_probability": 0.9988888888888889,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 17,
          "coverage_all_cases": 0.9444444444444444,
          "coverage_success_only": 0.9444444444444444,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 18,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 18,
        "p50": 307.6306045000008,
        "p95": 356.7956205999991,
        "p99": 360.2575577199991
      }
    },
    "ordinal": {
      "n_cases": 15,
      "n_success": 15,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.0,
      "log_loss": 0.0,
      "ordinal_expected_score_mae": 0.0,
      "n_ordinal_success": 15,
      "mean_provider_confidence": 0.9993333333333333,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 15,
          "mean_probability": 1.0,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 15,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 15,
        "p50": 326.1807499999989,
        "p95": 373.9926749000014,
        "p99": 397.91900138000204
      }
    },
    "predicate": {
      "n_cases": 20,
      "n_success": 20,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.006010000000000001,
      "log_loss": 0.04117232942525084,
      "ordinal_expected_score_mae": null,
      "n_ordinal_success": 0,
      "mean_provider_confidence": null,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 1,
          "mean_probability": 0.8,
          "accuracy": 1.0
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 19,
          "mean_probability": 0.9689473684210528,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 7,
          "coverage_all_cases": 0.35,
          "coverage_success_only": 0.35,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.97,
          "n_accepted": 11,
          "coverage_all_cases": 0.55,
          "coverage_success_only": 0.55,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.96,
          "n_accepted": 18,
          "coverage_all_cases": 0.9,
          "coverage_success_only": 0.9,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.95,
          "n_accepted": 19,
          "coverage_all_cases": 0.95,
          "coverage_success_only": 0.95,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.8,
          "n_accepted": 20,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 20,
        "p50": 328.44706250000047,
        "p95": 397.8354357500012,
        "p99": 427.29712075000145
      }
    },
    "routing": {
      "n_cases": 24,
      "n_success": 24,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.0003000000000000003,
      "log_loss": 0.0025781418215869802,
      "ordinal_expected_score_mae": null,
      "n_ordinal_success": 0,
      "mean_provider_confidence": 0.99625,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 24,
          "mean_probability": 0.9974999999999999,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 23,
          "coverage_all_cases": 0.9583333333333334,
          "coverage_success_only": 0.9583333333333334,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.94,
          "n_accepted": 24,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 24,
        "p50": 311.6983959999997,
        "p95": 382.45021605,
        "p99": 488.8562278599991
      }
    }
  },
  "by_variant": {
    "base": {
      "n_cases": 18,
      "n_success": 18,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.00037777777777777826,
      "log_loss": 0.006763164027416896,
      "ordinal_expected_score_mae": 0.0,
      "n_ordinal_success": 3,
      "mean_provider_confidence": 0.9992857142857143,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 18,
          "mean_probability": 0.9933333333333335,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 13,
          "coverage_all_cases": 0.7222222222222222,
          "coverage_success_only": 0.7222222222222222,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.99,
          "n_accepted": 14,
          "coverage_all_cases": 0.7777777777777778,
          "coverage_success_only": 0.7777777777777778,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 16,
          "coverage_all_cases": 0.8888888888888888,
          "coverage_success_only": 0.8888888888888888,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.97,
          "n_accepted": 17,
          "coverage_all_cases": 0.9444444444444444,
          "coverage_success_only": 0.9444444444444444,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.96,
          "n_accepted": 18,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 18,
        "p50": 309.58143800000016,
        "p95": 382.30753294999994,
        "p99": 382.44613939
      }
    },
    "distractor": {
      "n_cases": 18,
      "n_success": 18,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.00045555555555555605,
      "log_loss": 0.0073388744182805955,
      "ordinal_expected_score_mae": 0.0,
      "n_ordinal_success": 3,
      "mean_provider_confidence": 0.9992857142857143,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 18,
          "mean_probability": 0.9927777777777779,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 13,
          "coverage_all_cases": 0.7222222222222222,
          "coverage_success_only": 0.7222222222222222,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.99,
          "n_accepted": 14,
          "coverage_all_cases": 0.7777777777777778,
          "coverage_success_only": 0.7777777777777778,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 16,
          "coverage_all_cases": 0.8888888888888888,
          "coverage_success_only": 0.8888888888888888,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.96,
          "n_accepted": 18,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 18,
        "p50": 316.3879169999983,
        "p95": 372.0082150999998,
        "p99": 373.5133094199974
      }
    },
    "instruction_injection": {
      "n_cases": 18,
      "n_success": 18,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.0006666666666666674,
      "log_loss": 0.009060224429484684,
      "ordinal_expected_score_mae": 0.0,
      "n_ordinal_success": 3,
      "mean_provider_confidence": 0.9985714285714286,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 18,
          "mean_probability": 0.991111111111111,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 13,
          "coverage_all_cases": 0.7222222222222222,
          "coverage_success_only": 0.7222222222222222,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.99,
          "n_accepted": 14,
          "coverage_all_cases": 0.7777777777777778,
          "coverage_success_only": 0.7777777777777778,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.97,
          "n_accepted": 16,
          "coverage_all_cases": 0.8888888888888888,
          "coverage_success_only": 0.8888888888888888,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.96,
          "n_accepted": 17,
          "coverage_all_cases": 0.9444444444444444,
          "coverage_success_only": 0.9444444444444444,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.95,
          "n_accepted": 18,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 18,
        "p50": 319.4406250000004,
        "p95": 404.2957017500017,
        "p99": 406.08690674999934
      }
    },
    "option_order": {
      "n_cases": 11,
      "n_success": 11,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 7.27272727272728e-05,
      "log_loss": 0.0018366097561381333,
      "ordinal_expected_score_mae": null,
      "n_ordinal_success": 0,
      "mean_provider_confidence": 0.9981818181818182,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 11,
          "mean_probability": 0.9981818181818182,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 10,
          "coverage_all_cases": 0.9090909090909091,
          "coverage_success_only": 0.9090909090909091,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 11,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 11,
        "p50": 297.505791999999,
        "p95": 343.4053124999981,
        "p99": 357.57949609999895
      }
    },
    "paraphrase": {
      "n_cases": 18,
      "n_success": 18,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.005333333333333332,
      "log_loss": 0.023737281445853662,
      "ordinal_expected_score_mae": 0.0,
      "n_ordinal_success": 3,
      "mean_provider_confidence": 0.9885714285714285,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 1,
          "mean_probability": 0.8,
          "accuracy": 1.0
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 17,
          "mean_probability": 0.9882352941176471,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 11,
          "coverage_all_cases": 0.6111111111111112,
          "coverage_success_only": 0.6111111111111112,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 14,
          "coverage_all_cases": 0.7777777777777778,
          "coverage_success_only": 0.7777777777777778,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.96,
          "n_accepted": 16,
          "coverage_all_cases": 0.8888888888888888,
          "coverage_success_only": 0.8888888888888888,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.94,
          "n_accepted": 17,
          "coverage_all_cases": 0.9444444444444444,
          "coverage_success_only": 0.9444444444444444,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.8,
          "n_accepted": 18,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 18,
        "p50": 312.10370800000044,
        "p95": 384.2200795000005,
        "p99": 393.561749500001
      }
    },
    "whitespace": {
      "n_cases": 18,
      "n_success": 18,
      "n_failed": 0,
      "failure_counts": {},
      "accuracy_success_only": 1.0,
      "accuracy_all_cases": 1.0,
      "brier_multiclass": 0.00037777777777777826,
      "log_loss": 0.006763164027416896,
      "ordinal_expected_score_mae": 0.0,
      "n_ordinal_success": 3,
      "mean_provider_confidence": 0.9985714285714286,
      "calibration_top_probability": [
        {
          "lower": 0.0,
          "upper": 0.1,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.1,
          "upper": 0.2,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.2,
          "upper": 0.3,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.3,
          "upper": 0.4,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.4,
          "upper": 0.5,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.5,
          "upper": 0.6,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.6,
          "upper": 0.7,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.7,
          "upper": 0.8,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.8,
          "upper": 0.9,
          "n": 0,
          "mean_probability": null,
          "accuracy": null
        },
        {
          "lower": 0.9,
          "upper": 1.0,
          "n": 18,
          "mean_probability": 0.9933333333333335,
          "accuracy": 1.0
        }
      ],
      "risk_coverage": [
        {
          "threshold_top_probability": 1.0,
          "n_accepted": 13,
          "coverage_all_cases": 0.7222222222222222,
          "coverage_success_only": 0.7222222222222222,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.99,
          "n_accepted": 14,
          "coverage_all_cases": 0.7777777777777778,
          "coverage_success_only": 0.7777777777777778,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.98,
          "n_accepted": 16,
          "coverage_all_cases": 0.8888888888888888,
          "coverage_success_only": 0.8888888888888888,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.97,
          "n_accepted": 17,
          "coverage_all_cases": 0.9444444444444444,
          "coverage_success_only": 0.9444444444444444,
          "risk": 0.0
        },
        {
          "threshold_top_probability": 0.96,
          "n_accepted": 18,
          "coverage_all_cases": 1.0,
          "coverage_success_only": 1.0,
          "risk": 0.0
        }
      ],
      "latency_ms_attempted": {
        "n": 18,
        "p50": 299.00387450000034,
        "p95": 447.5577670500011,
        "p99": 506.01612060999923
      }
    }
  },
  "paired_robustness": {
    "distractor": {
      "n_pairs": 18,
      "n_complete_pairs": 18,
      "accuracy_delta_variant_minus_base": 0.0,
      "accuracy_delta_all_pairs_failures_incorrect": 0.0,
      "prediction_flip_rate": 0.0,
      "mean_total_variation": 0.0005555555555555559
    },
    "instruction_injection": {
      "n_pairs": 18,
      "n_complete_pairs": 18,
      "accuracy_delta_variant_minus_base": 0.0,
      "accuracy_delta_all_pairs_failures_incorrect": 0.0,
      "prediction_flip_rate": 0.0,
      "mean_total_variation": 0.002222222222222224
    },
    "option_order": {
      "n_pairs": 11,
      "n_complete_pairs": 11,
      "accuracy_delta_variant_minus_base": 0.0,
      "accuracy_delta_all_pairs_failures_incorrect": 0.0,
      "prediction_flip_rate": 0.0,
      "mean_total_variation": 0.0009090909090909096
    },
    "paraphrase": {
      "n_pairs": 18,
      "n_complete_pairs": 18,
      "accuracy_delta_variant_minus_base": 0.0,
      "accuracy_delta_all_pairs_failures_incorrect": 0.0,
      "prediction_flip_rate": 0.0,
      "mean_total_variation": 0.01666666666666667
    },
    "whitespace": {
      "n_pairs": 18,
      "n_complete_pairs": 18,
      "accuracy_delta_variant_minus_base": 0.0,
      "accuracy_delta_all_pairs_failures_incorrect": 0.0,
      "prediction_flip_rate": 0.0,
      "mean_total_variation": 0.0
    }
  },
  "usage": {
    "input_tokens_reported": 38936,
    "output_tokens_reported": 3643,
    "n_success_with_input_usage": 101
  },
  "notes": [
    "Original authored synthetic diagnostics; not a representative benchmark.",
    "Baseline is uniform probabilities, label-blind; not Jev outputs.",
    "Class prediction uses argmax; ties are class-order deterministic except provider Choice ties.",
    "Score MAE uses probability-weighted level index; Score accuracy uses modal level.",
    "Brier is sum over classes (binary included); log loss clips at 1e-15; both success-only.",
    "Calibration uses top-class probability, NOT provider confidence; ten fixed bins; final bin includes one.",
    "Risk coverage admits tied top probabilities together; failures never accepted.",
    "Latency percentiles use linear interpolation over attempted calls, including failed calls.",
    "Baseline latency is a zero placeholder, not a speed measurement.",
    "Paired families are correlated; no statistical significance or generalization claim.",
    "Receipts are local provenance records, not cryptographic provider attestations.",
    "Usage excludes failed calls; reported tokens are not a billing reconciliation."
  ]
}
```
