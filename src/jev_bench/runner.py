"""Private receipts, bounded orchestration, strict replay, allowlisted reports."""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from datetime import datetime, timezone
from . import __version__
from .core import (ValidationError, exact, number, parse_response, request_for,
                   require, strict_json, uniform_baseline, validate_dataset)
from .metrics import summarize, robustness
from .transport import bounded_request, MIN_TIMEOUT_SECONDS

FAILURES = {"http_error", "timeout", "network_error", "missing_key", "request_too_large",
            "response_too_large", "invalid_response", "budget_exhausted"}
MODEL_PATTERN = r"jev-(?:[0-9]+\.[0-9]+\.[0-9]+|latest|preview)"
MAX_RETAINED_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_RECEIPT_BYTES = 32000000


def encoded(value):
    # Preserve object order: choice-order perturbations must change request hashes.
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def code_digest():
    h = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        h.update(path.name.encode()); h.update(path.read_bytes())
    return h.hexdigest()


def bounds_valid(mode, model, bounds):
    exact(bounds, {"max_requests", "max_seconds", "request_timeout"})
    require(mode in ("baseline", "live"), "invalid_mode")
    require(type(bounds["max_requests"]) is int and 0 <= bounds["max_requests"] <= 1000, "request_budget")
    number(bounds["max_seconds"], MIN_TIMEOUT_SECONDS, 900)
    number(bounds["request_timeout"], MIN_TIMEOUT_SECONDS, 120)
    if mode == "live":
        require(type(model) is str and re.fullmatch(MODEL_PATTERN, model) is not None, "explicit_model_required")
        require(bounds["max_requests"] > 0, "request_budget")
    else:
        require(model is None and bounds["max_requests"] == 0, "baseline_config")


def private_directory(path):
    path = Path(path).expanduser().resolve()
    source_root = Path(__file__).resolve().parents[2]
    require(path != source_root and source_root not in path.parents, "raw_inside_repository")
    require(not any((parent / ".git").exists() for parent in (path,) + tuple(path.parents)),
            "raw_inside_repository")
    require(not path.exists(), "raw_directory_must_be_new")
    path.mkdir(parents=True, mode=0o700)
    os.chmod(path, 0o700)
    return path


def save_receipt(path, value):
    raw = encoded(value)
    require(len(raw) <= MAX_RECEIPT_BYTES, "receipt_too_large")
    fd, name = tempfile.mkstemp(prefix=".receipt-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(raw); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def run(dataset, mode, raw_dir, model=None, max_requests=0, max_seconds=180, request_timeout=15):
    dataset = validate_dataset(dataset)
    bounds = {"max_requests": max_requests, "max_seconds": max_seconds, "request_timeout": request_timeout}
    bounds_valid(mode, model, bounds)
    if mode == "live":
        require(bool(os.environ.get("TYPESAFE_API_KEY")), "missing_key")
    folder = private_directory(raw_dir)
    receipt = {"schema_version": 2, "harness_version": __version__, "code_sha256": code_digest(),
               "dataset_sha256": digest(dataset), "mode": mode, "requested_model": model,
               "bounds": bounds, "records": [],
               "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z"),
               "completed_at_utc": None}
    deadline, calls = time.monotonic() + max_seconds, 0
    retained_response_bytes = 0
    for case in dataset["cases"]:
        inp = case["input"]
        request = request_for(inp, model) if mode == "live" else None
        record = {"case_id": case["id"], "request_sha256": digest(request) if request else None,
                  "status": "budget_exhausted", "latency_ms": None, "http_status": None,
                  "response": None, "baseline_prediction": None}
        remaining = deadline - time.monotonic()
        if mode == "baseline":
            record.update(status="ok", latency_ms=0.0, baseline_prediction=uniform_baseline(inp))
        elif remaining >= MIN_TIMEOUT_SECONDS and calls < max_requests:
            calls += 1
            start = time.monotonic()
            result = bounded_request(request, min(request_timeout, remaining))
            record["latency_ms"] = (time.monotonic() - start) * 1000
            status = result.get("status")
            require(status in FAILURES | {"ok"}, "transport_status")
            record["status"] = status
            if status == "ok":
                try:
                    parse_response(inp, result.get("response"))
                    if model not in ("jev-latest", "jev-preview"):
                        require(result["response"]["model"] == model, "resolved_model_mismatch")
                    response_bytes = len(encoded(result["response"]))
                    if retained_response_bytes + response_bytes > MAX_RETAINED_RESPONSE_BYTES:
                        record["status"] = "response_too_large"
                    else:
                        record["response"] = result["response"]
                        retained_response_bytes += response_bytes
                except (ValueError, TypeError, OverflowError, RecursionError):
                    # ValidationError is a ValueError; serialization defects are
                    # equally invalid responses, not checkpoint/orchestration errors.
                    record["status"] = "invalid_response"
            elif status == "http_error":
                record["http_status"] = result.get("http_status")
        receipt["records"].append(record)
        # Partial checkpoints are private and deliberately not valid final replay receipts.
        save_receipt(folder / "receipt.json", receipt)
    receipt["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    validate_receipt(dataset, receipt)
    save_receipt(folder / "receipt.json", receipt)
    return receipt


def validate_receipt(dataset, receipt):
    validate_dataset(dataset)
    exact(receipt, {"schema_version", "harness_version", "code_sha256", "dataset_sha256",
                    "mode", "requested_model", "bounds", "records", "started_at_utc", "completed_at_utc"})
    require(type(receipt["schema_version"]) is int and receipt["schema_version"] == 2)
    for field in ("started_at_utc", "completed_at_utc"):
        stamp = receipt[field]
        require(type(stamp) is str and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6}Z", stamp) is not None,
                "receipt_timestamp")
        try:
            datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        except ValueError:
            raise ValidationError("receipt_timestamp") from None
    require(receipt["harness_version"] == __version__, "receipt_version")
    require(type(receipt["code_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", receipt["code_sha256"]) is not None)
    require(receipt["dataset_sha256"] == digest(dataset), "dataset_mismatch")
    mode, model = receipt["mode"], receipt["requested_model"]
    bounds_valid(mode, model, receipt["bounds"])
    records = receipt["records"]
    require(type(records) is list and len(records) == len(dataset["cases"]), "missing_cases")
    rows, attempted = [], 0
    for case, rec in zip(dataset["cases"], records):
        exact(rec, {"case_id", "request_sha256", "status", "latency_ms", "http_status", "response", "baseline_prediction"})
        require(rec["case_id"] == case["id"], "case_order_or_duplicate")
        require(rec["status"] in FAILURES | {"ok"}, "receipt_status")
        if rec["latency_ms"] is not None:
            number(rec["latency_ms"], 0, 1000000)
            attempted += 1
        require((rec["latency_ms"] is None) == (rec["status"] == "budget_exhausted"), "attempt_latency")
        if rec["status"] == "http_error":
            require(type(rec["http_status"]) is int and 100 <= rec["http_status"] <= 599 and rec["http_status"] != 200)
        else:
            require(rec["http_status"] is None)
        pred = None
        if mode == "baseline":
            require(rec["request_sha256"] is None and rec["response"] is None and rec["status"] == "ok")
            pred = uniform_baseline(case["input"])
            require(rec["baseline_prediction"] == pred, "baseline_prediction_mismatch")
        else:
            require(rec["request_sha256"] == digest(request_for(case["input"], model)), "request_mismatch")
            require(rec["baseline_prediction"] is None)
            if rec["status"] == "ok":
                pred = parse_response(case["input"], rec["response"])
                if model not in ("jev-latest", "jev-preview"):
                    require(rec["response"]["model"] == model, "resolved_model_mismatch")
            else:
                require(rec["response"] is None, "failure_body_forbidden")
        rows.append({"case": case, "status": rec["status"], "prediction": pred, "latency_ms": rec["latency_ms"]})
    if mode == "live":
        require(attempted <= receipt["bounds"]["max_requests"], "request_budget_exceeded")
    return rows


def load_receipt(dataset, path):
    # Bounded even if the file grows after opening; never read_bytes() first.
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_RECEIPT_BYTES + 1)
    require(len(raw) <= MAX_RECEIPT_BYTES, "receipt_too_large")
    receipt = strict_json(raw)
    validate_receipt(dataset, receipt)
    return receipt


def report(dataset, receipt):
    rows = validate_receipt(dataset, receipt)
    good = [r["response"] for r in receipt["records"] if r["response"] is not None]
    # Export allowlist constructed from validated numeric summaries, NEVER raw dict merges.
    return {"report_schema_version": 1, "harness_version": __version__, "code_sha256": receipt["code_sha256"],
            "dataset_sha256": receipt["dataset_sha256"], "mode": receipt["mode"],
            "requested_model": receipt["requested_model"],
            "resolved_models": sorted({r["model"] for r in good}),
            "dataset_provenance": "original-authored-synthetic-diagnostic",
            "summary": summarize(rows),
            "by_task": {task: summarize([r for r in rows if r["case"]["task"] == task])
                        for task in sorted({r["case"]["task"] for r in rows})},
            "by_variant": {variant: summarize([r for r in rows if r["case"]["variant"] == variant])
                           for variant in sorted({r["case"]["variant"] for r in rows})},
            "paired_robustness": robustness(rows),
            "usage": {"input_tokens_reported": sum(r["usage"].get("input_tokens") or 0 for r in good),
                      "output_tokens_reported": sum(r["usage"].get("output_tokens") or 0 for r in good),
                      "n_success_with_input_usage": sum(r["usage"].get("input_tokens") is not None for r in good)},
            "notes": ["Original authored synthetic diagnostics; not a representative benchmark.",
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
                      "Usage excludes failed calls; reported tokens are not a billing reconciliation."]}


def markdown(value):
    title = "Not Jev results: offline uniform baseline" if value["mode"] == "baseline" else "Jev live diagnostic results"
    lines = ["# " + title, "", "Dataset SHA-256: `" + value["dataset_sha256"] + "`", "",
             "| Task | Cases | Success | Accuracy (all) | Brier (success) | Log loss (success) |",
             "|---|---:|---:|---:|---:|---:|"]
    for task, stats in value["by_task"].items():
        def fmt(x): return "N/A" if x is None else "%.6f" % x
        lines.append("| %s | %d | %d | %s | %s | %s |" % (task, stats["n_cases"], stats["n_success"],
            fmt(stats["accuracy_all_cases"]), fmt(stats["brier_multiclass"]), fmt(stats["log_loss"])))
    lines += ["", "## Interpretation", ""] + ["- " + note for note in value["notes"]]
    lines += ["", "## Complete sanitized metrics", "", "```json", json.dumps(value, indent=2, allow_nan=False), "```", ""]
    return "\n".join(lines)
