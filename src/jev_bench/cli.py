"""CLI never accepts keys, alternate endpoints, or automatic retry settings."""
import argparse
import json
from pathlib import Path
import sys
from .core import ValidationError, require, strict_json, validate_dataset
from .runner import load_receipt, markdown, report, run


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValidationError("invalid_arguments")


def main(argv=None):
    try:
        parser = SafeParser(description="Original synthetic Jev diagnostics; offline baseline is not Jev inference.")
        commands = parser.add_subparsers(dest="command", required=True)
        for command in ("baseline", "live", "replay"):
            sub = commands.add_parser(command)
            sub.add_argument("--dataset", required=True, type=Path)
            sub.add_argument("--export-dir", required=True, type=Path, help="New directory for allowlisted JSON/Markdown")
            if command == "replay":
                sub.add_argument("--receipt", required=True, type=Path)
            else:
                sub.add_argument("--raw-dir", required=True, type=Path, help="New private directory outside every Git repository")
            if command == "live":
                sub.add_argument("--model", required=True, help="Explicit ID from current docs/models, e.g. jev-1.13.0")
                sub.add_argument("--max-requests", required=True, type=int, help="1..1000; no retry; remaining cases counted as failures")
                sub.add_argument("--max-seconds", required=True, type=float, help="Total request window, at most 900 seconds")
                sub.add_argument("--request-timeout", type=float, default=15, help="Hard worker deadline, at most 120 seconds")
        args = parser.parse_args(argv)
        require(not args.export_dir.exists(), "export_directory_must_be_new")
        require(args.dataset.stat().st_size <= 4000000, "dataset_too_large")
        dataset = validate_dataset(strict_json(args.dataset.read_bytes()))
        if args.command == "replay":
            receipt = load_receipt(dataset, args.receipt)
        elif args.command == "live":
            receipt = run(dataset, "live", args.raw_dir, args.model, args.max_requests,
                          args.max_seconds, args.request_timeout)
        else:
            receipt = run(dataset, "baseline", args.raw_dir)
        value = report(dataset, receipt)
        args.export_dir.mkdir(parents=True, mode=0o700)
        (args.export_dir / "report.json").write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        (args.export_dir / "report.md").write_text(markdown(value), encoding="utf-8")
        print("Report written: %d cases, %d successful, %d failed." %
              (value["summary"]["n_cases"], value["summary"]["n_success"], value["summary"]["n_failed"]))
        return 0 if value["summary"]["n_failed"] == 0 else 3
    except (ValidationError, OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError):
        print("Benchmark rejected: invalid configuration, input, receipt, or output path. See --help.", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Benchmark interrupted; partial private receipt is not replayable.", file=sys.stderr)
        return 130
