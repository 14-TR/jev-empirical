import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from jev_bench.core import strict_json, validate_dataset

ROOT = Path(__file__).resolve().parents[1]


class CliDatasetTests(unittest.TestCase):
    def test_original_diagnostics_cover_five_tasks_and_perturbations(self):
        path = ROOT/"datasets"/"synthetic_diagnostics.json"
        self.assertTrue(path.exists(), "authored synthetic diagnostics missing")
        data = validate_dataset(strict_json(path.read_bytes()))
        tasks = Counter(c["task"] for c in data["cases"])
        self.assertEqual(set(tasks), {"routing", "evidence", "candidate", "predicate", "ordinal"})
        self.assertEqual(len(data["cases"]), 101)
        self.assertEqual(sum(c["variant"] == "base" for c in data["cases"]), 18)
        self.assertEqual({c["variant"] for c in data["cases"]},
                         {"base", "paraphrase", "whitespace", "distractor", "instruction_injection", "option_order"})

    def test_cli_offline_and_replay_agree_without_credentials(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            env = dict(os.environ, PYTHONPATH=str(ROOT/"src")); env.pop("TYPESAFE_API_KEY", None)
            base = [sys.executable, "-m", "jev_bench"]
            run = subprocess.run(base+["baseline", "--dataset", str(ROOT/"datasets/synthetic_diagnostics.json"),
                "--raw-dir", str(folder/"raw"), "--export-dir", str(folder/"export")],
                env=env, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            rep = subprocess.run(base+["replay", "--dataset", str(ROOT/"datasets/synthetic_diagnostics.json"),
                "--receipt", str(folder/"raw/receipt.json"), "--export-dir", str(folder/"replay")],
                env=env, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(rep.returncode, 0, rep.stderr)
            report = json.loads((folder/"export/report.json").read_text())
            self.assertEqual(report, json.loads((folder/"replay/report.json").read_text()))
            self.assertEqual(report["summary"]["n_cases"], 101)
            self.assertIn("Not Jev results", (folder/"export/report.md").read_text())

    def test_cli_missing_explicit_live_configuration_never_calls_network(self):
        env = dict(os.environ, PYTHONPATH=str(ROOT/"src")); env.pop("TYPESAFE_API_KEY", None)
        for args in (["live"], ["live", "--api-key", "SECRET-MARKER"]):
            p = subprocess.run([sys.executable, "-m", "jev_bench"] + args,
                env=env, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2)
            self.assertNotIn("SECRET-MARKER", p.stdout+p.stderr)
            self.assertNotIn("Traceback", p.stderr)
