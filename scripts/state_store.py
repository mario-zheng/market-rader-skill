#!/usr/bin/env python3
"""Persistent profile, observation, and run-state store for market-radar."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import unicodedata
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


WORKFLOWS = {"material_prices", "market_balance"}
CONFIRMATION_BASES = {"user_choice", "explicit_user_confirmation", "cached_user_choice"}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return "".join(char for char in value if char.isalnum())


def digest(value: str, length: int = 20) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def atomic_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def profile_path(data_dir: Path, product_id: str) -> Path:
    return data_dir / "profiles" / f"{digest(product_id)}.json"


def validate_profile(profile: dict[str, Any]) -> None:
    for field in ("product_id", "canonical_name"):
        if not isinstance(profile.get(field), str) or not profile[field].strip():
            raise ValueError(f"Profile requires non-empty {field}")
    if not isinstance(profile.get("aliases", []), list):
        raise ValueError("Profile aliases must be a list")
    if not isinstance(profile.get("subcategory_path", []), list):
        raise ValueError("Profile subcategory_path must be a list")
    classification = profile.get("classification", {})
    if classification.get("status") == "confirmed":
        if classification.get("confirmation_basis") not in CONFIRMATION_BASES:
            raise ValueError(f"Confirmed classification requires confirmation_basis in {sorted(CONFIRMATION_BASES)}")
        if not profile.get("subcategory_path"):
            raise ValueError("Confirmed classification requires a non-empty subcategory_path")


def gate_result(data_dir: Path, product_id: str) -> dict[str, Any]:
    path = profile_path(data_dir, product_id)
    if not path.exists():
        return {"product_id": product_id, "gate_open": False, "reason": "profile_not_found"}
    profile = read_json(path)
    classification = profile.get("classification", {})
    if classification.get("status") != "confirmed":
        return {"product_id": product_id, "gate_open": False, "reason": "classification_not_confirmed"}
    if classification.get("confirmation_basis") not in CONFIRMATION_BASES:
        return {"product_id": product_id, "gate_open": False, "reason": "missing_user_confirmation"}
    if not profile.get("subcategory_path"):
        return {"product_id": product_id, "gate_open": False, "reason": "subcategory_path_empty"}
    return {
        "product_id": product_id,
        "gate_open": True,
        "subcategory_path": profile["subcategory_path"],
        "confirmation_basis": classification["confirmation_basis"],
    }


def reuse_result(profile: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    classification = profile.get("classification", {})
    if classification.get("status") != "confirmed" or not profile.get("subcategory_path"):
        missing.append("classification")
    if profile.get("bom", {}).get("status") != "confirmed":
        missing.append("bom")
    return {
        "reuse_ready": not missing,
        "missing_reuse_fields": missing,
        "display_name": " / ".join(
            [
                str(profile.get("canonical_name", "")),
                *[str(item) for item in profile.get("subcategory_path", [])],
                *([str(profile["specification"])] if profile.get("specification") else []),
            ]
        ),
    }


def find_profile(args: argparse.Namespace) -> None:
    profiles_dir = args.data_dir / "profiles"
    query = normalized(args.product)
    matches: list[dict[str, Any]] = []
    if profiles_dir.exists():
        for path in profiles_dir.glob("*.json"):
            profile = read_json(path)
            names = [profile.get("canonical_name", ""), profile.get("product_id", "")]
            names.extend(profile.get("aliases", []))
            names.extend(profile.get("subcategory_path", []))
            normalized_names = {normalized(str(item)) for item in names if item}
            exact = query in normalized_names
            partial = any(query and item and (query in item or item in query) for item in normalized_names)
            if exact or partial:
                matches.append({**profile, **reuse_result(profile), "match_type": "exact" if exact else "partial"})
    matches.sort(key=lambda item: (item.get("match_type") != "exact", not item.get("reuse_ready"), item.get("display_name", "")))
    print(json.dumps({"query": args.product, "matches": matches}, ensure_ascii=False, indent=2))


def save_profile(args: argparse.Namespace) -> None:
    incoming = read_json(args.input)
    validate_profile(incoming)
    incoming.setdefault("schema_version", "1.0")
    path = profile_path(args.data_dir, incoming["product_id"])
    timestamp = now_iso()
    if path.exists():
        current = read_json(path)
        history = list(current.get("revisions", []))
        prior = {key: value for key, value in current.items() if key != "revisions"}
        prior["superseded_at"] = timestamp
        history.append(prior)
        aliases = sorted({str(item) for item in current.get("aliases", []) + incoming.get("aliases", [])})
        merged = {**current, **incoming, "aliases": aliases, "revisions": history}
        merged["created_at"] = current.get("created_at", timestamp)
    else:
        merged = {**incoming, "revisions": list(incoming.get("revisions", [])), "created_at": timestamp}
    merged["updated_at"] = timestamp
    atomic_write(path, merged)
    print(json.dumps({"saved": str(path), "product_id": merged["product_id"]}, ensure_ascii=False))


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    for field in ("product_id", "as_of", "scope_key"):
        if not isinstance(snapshot.get(field), str) or not snapshot[field].strip():
            raise ValueError(f"Snapshot requires non-empty {field}")
    if snapshot.get("workflow") not in WORKFLOWS:
        raise ValueError(f"workflow must be one of {sorted(WORKFLOWS)}")
    if not isinstance(snapshot.get("metrics"), list):
        raise ValueError("Snapshot metrics must be a list")
    for metric in snapshot["metrics"]:
        if not isinstance(metric, dict) or not metric.get("metric_key"):
            raise ValueError("Every metric requires metric_key")


def append_snapshot(args: argparse.Namespace) -> None:
    snapshot = read_json(args.input)
    validate_snapshot(snapshot)
    gate = gate_result(args.data_dir, snapshot["product_id"])
    if not gate["gate_open"]:
        raise ValueError(f"Classification gate is closed: {gate['reason']}")
    snapshot.setdefault("schema_version", "1.0")
    timestamp = now_iso()
    snapshot.setdefault("created_at", timestamp)
    snapshot["updated_at"] = timestamp
    folder = args.data_dir / "observations" / digest(snapshot["product_id"]) / snapshot["workflow"]
    filename = f"{snapshot['as_of']}_{digest(snapshot['scope_key'], 12)}.json"
    path = folder / filename
    existed = path.exists()
    if existed:
        current = read_json(path)
        snapshot["created_at"] = current.get("created_at", snapshot["created_at"])
    atomic_write(path, snapshot)
    print(json.dumps({"saved": str(path), "updated_existing": existed}, ensure_ascii=False))


def classification_gate(args: argparse.Namespace) -> None:
    print(json.dumps(gate_result(args.data_dir, args.product_id), ensure_ascii=False, indent=2))


def series(args: argparse.Namespace) -> None:
    folder = args.data_dir / "observations" / digest(args.product_id) / args.workflow
    groups: dict[str, list[dict[str, Any]]] = {}
    if folder.exists():
        for path in sorted(folder.glob("*.json")):
            snapshot = read_json(path)
            if args.scope_key and snapshot.get("scope_key") != args.scope_key:
                continue
            for metric in snapshot.get("metrics", []):
                if metric.get("metric_key") != args.metric_key:
                    continue
                scope = snapshot.get("scope_key", "")
                groups.setdefault(scope, []).append(
                    {
                        "as_of": snapshot.get("as_of"),
                        "value": metric.get("value"),
                        "low": metric.get("low"),
                        "high": metric.get("high"),
                        "unit": metric.get("unit"),
                        "currency": metric.get("currency"),
                        "period": metric.get("period"),
                    }
                )
    output = []
    for scope, points in groups.items():
        by_date = {str(point["as_of"]): point for point in points if point.get("as_of")}
        ordered = [by_date[key] for key in sorted(by_date)]
        output.append(
            {
                "scope_key": scope,
                "metric_key": args.metric_key,
                "distinct_dates": len(ordered),
                "trend_eligible": len(ordered) >= 2,
                "points": ordered,
            }
        )
    print(json.dumps({"series": output}, ensure_ascii=False, indent=2))


def parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def metric_points(args: argparse.Namespace) -> list[dict[str, Any]]:
    folder = args.data_dir / "observations" / digest(args.product_id) / args.workflow
    by_date: dict[date, dict[str, Any]] = {}
    if not folder.exists():
        return []
    for path in sorted(folder.glob("*.json")):
        snapshot = read_json(path)
        if args.scope_key and snapshot.get("scope_key") != args.scope_key:
            continue
        observed = parse_date(snapshot.get("as_of"))
        if observed is None:
            continue
        for metric in snapshot.get("metrics", []):
            if metric.get("metric_key") != args.metric_key:
                continue
            value = numeric(metric.get("value"))
            if value is None:
                continue
            by_date[observed] = {
                "as_of": observed.isoformat(),
                "value": value,
                "unit": metric.get("unit"),
                "currency": metric.get("currency"),
                "scope_key": snapshot.get("scope_key"),
            }
    return [by_date[key] for key in sorted(by_date)]


def compare(args: argparse.Namespace) -> None:
    points = metric_points(args)
    requested_as_of = parse_date(args.as_of) if args.as_of else None
    if requested_as_of:
        points = [point for point in points if parse_date(point["as_of"]) <= requested_as_of]
    if not points:
        print(json.dumps({"metric_key": args.metric_key, "status": "no_current_value", "comparisons": []}, ensure_ascii=False, indent=2))
        return

    current = points[-1]
    current_date = parse_date(current["as_of"])
    tolerances = {7: 3, 30: 7}
    comparisons: list[dict[str, Any]] = []
    for window in args.windows:
        target = current_date - timedelta(days=window)
        candidates = [point for point in points[:-1] if parse_date(point["as_of"]) < current_date]
        baseline = min(candidates, key=lambda point: abs((parse_date(point["as_of"]) - target).days)) if candidates else None
        tolerance = tolerances.get(window, max(1, round(window * 0.25)))
        distance = abs((parse_date(baseline["as_of"]) - target).days) if baseline else None
        label = "week" if window == 7 else "month" if window == 30 else f"{window}_days"
        if baseline is None or distance > tolerance:
            comparisons.append({"label": label, "days": window, "status": "no_comparable_history", "target_date": target.isoformat(), "tolerance_days": tolerance})
            continue
        absolute_change = current["value"] - baseline["value"]
        percent_change = None if baseline["value"] == 0 else absolute_change / baseline["value"] * 100
        comparisons.append(
            {
                "label": label,
                "days": window,
                "status": "comparable",
                "current_as_of": current["as_of"],
                "current_value": current["value"],
                "baseline_as_of": baseline["as_of"],
                "baseline_value": baseline["value"],
                "absolute_change": absolute_change,
                "percent_change": percent_change,
                "unit": current.get("unit"),
                "currency": current.get("currency"),
                "scope_key": current.get("scope_key"),
            }
        )
    print(json.dumps({"metric_key": args.metric_key, "status": "ok", "current": current, "comparisons": comparisons}, ensure_ascii=False, indent=2))


def save_run(args: argparse.Namespace) -> None:
    state = read_json(args.input)
    run_id = state.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("Run state requires run_id")
    timestamp = now_iso()
    path = args.data_dir / "runs" / digest(run_id) / "state.json"
    if path.exists():
        state.setdefault("created_at", read_json(path).get("created_at", timestamp))
    else:
        state.setdefault("created_at", timestamp)
    state["updated_at"] = timestamp
    atomic_write(path, state)
    print(json.dumps({"saved": str(path), "run_id": run_id}, ensure_ascii=False))


def load_run(args: argparse.Namespace) -> None:
    path = args.data_dir / "runs" / digest(args.run_id) / "state.json"
    if not path.exists():
        print(json.dumps({"run_id": args.run_id, "found": False}, ensure_ascii=False))
        return
    print(json.dumps({"run_id": args.run_id, "found": True, "state": read_json(path)}, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)

    def common(name: str, handler: Any) -> argparse.ArgumentParser:
        command = subparsers.add_parser(name)
        command.add_argument("--data-dir", type=Path, required=True)
        command.set_defaults(handler=handler)
        return command

    command = common("find-profile", find_profile)
    command.add_argument("--product", required=True)

    command = common("save-profile", save_profile)
    command.add_argument("--input", type=Path, required=True)

    command = common("append-snapshot", append_snapshot)
    command.add_argument("--input", type=Path, required=True)

    command = common("classification-gate", classification_gate)
    command.add_argument("--product-id", required=True)

    command = common("series", series)
    command.add_argument("--product-id", required=True)
    command.add_argument("--workflow", choices=sorted(WORKFLOWS), required=True)
    command.add_argument("--metric-key", required=True)
    command.add_argument("--scope-key")

    command = common("compare", compare)
    command.add_argument("--product-id", required=True)
    command.add_argument("--workflow", choices=sorted(WORKFLOWS), required=True)
    command.add_argument("--metric-key", required=True)
    command.add_argument("--scope-key")
    command.add_argument("--as-of")
    command.add_argument("--windows", type=int, nargs="+", default=[7, 30])

    command = common("save-run", save_run)
    command.add_argument("--input", type=Path, required=True)

    command = common("load-run", load_run)
    command.add_argument("--run-id", required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    args.data_dir = args.data_dir.resolve()
    args.handler(args)


if __name__ == "__main__":
    main()
