"""Strict local data contract; evaluation labels stay outside model inputs."""
import copy
import json
import math
import re


class ValidationError(ValueError):
    """Messages are fixed codes, never values from untrusted input."""


def require(condition, code="invalid_data"):
    if not condition:
        raise ValidationError(code)


def exact(value, keys):
    require(type(value) is dict and set(value) == set(keys))


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result
    def nonfinite(_):
        raise ValidationError("nonfinite_json")
    def finite_float(text):
        value = float(text)
        require(math.isfinite(value), "nonfinite_json")
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite,
                          parse_float=finite_float)
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise ValidationError("invalid_json") from None


def token(value):
    return type(value) is str and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,79}", value) is not None


def validate_input(value):
    exact(value, {"state", "question"})
    # Intentionally narrow v1 state surface: no generic record/label dictionaries.
    exact(value["state"], {"text"})
    require(type(value["state"]["text"]) is str and 0 < len(value["state"]["text"]) <= 16000)
    q = value["question"]
    exact(q, {"type", "instructions", "criteria"})
    require(q["type"] in ("choice", "score", "noul"))
    require(type(q["instructions"]) is str and 0 < len(q["instructions"]) <= 4000)
    criteria = q["criteria"]
    if q["type"] == "score":
        require(type(criteria) is list and 2 <= len(criteria) <= 10)
        descriptions = criteria
    else:
        require(type(criteria) is dict and 2 <= len(criteria) <= 20)
        require(all(token(k) for k in criteria))
        if q["type"] == "noul":
            require(set(criteria) == {"true", "false"})
        descriptions = list(criteria.values())
    require(all(type(d) is str and 0 < len(d) <= 2000 for d in descriptions))
    return value


def classes(model_input):
    q = model_input["question"]
    if q["type"] == "score":
        return [str(i) for i in range(len(q["criteria"]))]
    if q["type"] == "noul":
        return ["false", "true"]
    return sorted(q["criteria"])


def validate_dataset(value):
    exact(value, {"schema_version", "provenance", "name", "cases"})
    require(type(value["schema_version"]) is int and value["schema_version"] == 1)
    require(value["provenance"] == "original-authored-synthetic-diagnostic")
    require(token(value["name"]))
    cases = value["cases"]
    require(type(cases) is list and 0 < len(cases) <= 1000)
    seen, groups = set(), {}
    for case in cases:
        exact(case, {"id", "task", "pair_id", "variant", "input", "gold"})
        require(all(token(case[k]) for k in ("id", "task", "pair_id", "variant")))
        require(case["task"] in ("routing", "evidence", "candidate", "predicate", "ordinal"), "unknown_task")
        require(case["variant"] in ("base", "paraphrase", "whitespace", "distractor", "instruction_injection", "option_order"), "unknown_variant")
        require(case["id"] not in seen)
        seen.add(case["id"])
        validate_input(case["input"])
        require(type(case["gold"]) is str and case["gold"] in classes(case["input"]))
        group = groups.setdefault(case["pair_id"], {})
        require(case["variant"] not in group)
        group[case["variant"]] = case
    for group in groups.values():
        require("base" in group)
        base = group["base"]
        for case in group.values():
            require(case["task"] == base["task"] and case["gold"] == base["gold"])
            require(case["input"]["question"]["type"] == base["input"]["question"]["type"])
            require(classes(case["input"]) == classes(base["input"]))
    return copy.deepcopy(value)


def number(value, low=0.0, high=1.0):
    # Compare bounded integers before float conversion (arbitrary precision JSON).
    require(type(value) in (int, float) and low <= value <= high and math.isfinite(value),
            "invalid_number")
    return float(value)


def distribution(model_input, probabilities):
    exact(probabilities, classes(model_input))
    p = {key: number(value) for key, value in probabilities.items()}
    require(abs(sum(p.values()) - 1.0) <= 1e-6, "probability_sum")
    return p


def prediction(model_input, p, confidence=None, selected=None):
    keys = classes(model_input)
    predicted = selected if selected is not None else max(keys, key=lambda key: p[key])
    expected = (sum(int(k) * p[k] for k in keys)
                if model_input["question"]["type"] == "score" else None)
    return {"probabilities": p, "predicted": predicted,
            "provider_confidence": confidence, "expected_score": expected}


def uniform_baseline(model_input):
    validate_input(model_input)
    keys = classes(model_input)
    return prediction(model_input, {key: 1.0 / len(keys) for key in keys})


def parse_response(model_input, raw):
    validate_input(model_input)
    require(type(raw) is dict and {"model", "answers", "usage"} <= set(raw), "response_shape")
    require(type(raw["model"]) is str and
            re.fullmatch(r"jev-(?:[0-9]+\.[0-9]+\.[0-9]+|latest|preview)", raw["model"]) is not None,
            "response_model")
    exact(raw["answers"], {"q"})
    require(type(raw["usage"]) is dict, "usage_shape")
    for field in ("input_tokens", "output_tokens"):
        v = raw["usage"].get(field)
        require(v is None or (type(v) is int and 0 <= v <= 1000000000), "usage_value")
    answer = raw["answers"]["q"]
    kind = model_input["question"]["type"]
    require(type(answer) is dict and answer.get("type") == kind, "answer_type")
    if kind == "noul":
        require("noul" in answer, "missing_noul")
        p = number(answer["noul"])
        return prediction(model_input, {"false": 1.0 - p, "true": p})
    require({"probabilities", "confidence"} <= set(answer), "missing_probability")
    p = distribution(model_input, answer["probabilities"])
    confidence = number(answer["confidence"])
    if kind == "choice":
        selected = answer.get("choice")
        require(type(selected) is str and selected in p and p[selected] == max(p.values()),
                "choice_inconsistent")
        return prediction(model_input, p, confidence, selected)
    require({"score", "legend"} <= set(answer), "missing_score")
    expected_legend = {str(i): description for i, description in enumerate(model_input["question"]["criteria"])}
    require(answer["legend"] == expected_legend, "legend_mismatch")
    score = number(answer["score"], 0, len(p) - 1)
    result = prediction(model_input, p, confidence)
    require(abs(score - result["expected_score"]) <= 1e-5, "score_inconsistent")
    return result


def request_for(model_input, model):
    validate_input(model_input)
    require(token(model), "invalid_model")
    return {"state": copy.deepcopy(model_input["state"]), "model": model,
            "questions": {"q": copy.deepcopy(model_input["question"])}}
