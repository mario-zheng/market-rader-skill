#!/usr/bin/env python3
"""Render a self-contained market-radar dashboard from report JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MARKER = "__MARKET_RADAR_DATA__"

PLAIN_REPLACEMENTS = (
    ("上行", "上涨"),
    ("下行", "下跌"),
    ("主动补库", "需求增加且企业正在补充库存"),
    ("被动补库", "需求减少但库存仍在增加"),
    ("主动去库", "需求减少且企业正在减少库存"),
    ("被动去库", "需求增加但库存正在减少"),
    ("高位震荡", "价格目前较高，短期上下波动"),
    ("低位震荡", "价格目前较低，短期上下波动"),
    ("走强", "上涨或变贵"),
    ("走弱", "下跌或变便宜"),
    ("偏强", "上涨压力较大"),
    ("偏弱", "下跌压力较大"),
    ("承压", "面临下跌压力"),
    ("拐头", "方向可能发生变化"),
    ("底部特征明显", "价格较低，继续下跌空间暂不明确"),
    ("景气度", "市场活跃程度"),
    ("景气", "市场活跃"),
    ("趋势性强", "连续变化较明显"),
    ("震荡", "短期上下波动"),
    ("高位", "较高水平"),
    ("低位", "较低水平"),
)


def plain_language(value: object, subject: str = "相关产品") -> object:
    if isinstance(value, str):
        value = value.replace("利多", f"对{subject}价格上涨有推动")
        value = value.replace("利空", f"对{subject}价格下跌有推动")
        value = value.replace("走强", f"{subject}价格上涨")
        value = value.replace("走弱", f"{subject}价格下跌")
        value = value.replace("偏强", f"{subject}价格上涨压力较大")
        value = value.replace("偏弱", f"{subject}价格下跌压力较大")
        for source, target in PLAIN_REPLACEMENTS:
            if source in ("走强", "走弱", "偏强", "偏弱", "利多", "利空"):
                continue
            value = value.replace(source, target)
        return value
    if isinstance(value, list):
        return [plain_language(item, subject) for item in value]
    if isinstance(value, dict):
        return {key: plain_language(item, subject) for key, item in value.items()}
    return value


def plain_report(report: dict[str, object]) -> dict[str, object]:
    """Translate only analyst-facing judgement fields, not source evidence or names."""
    report = dict(report)
    product_name = str(report.get("product", {}).get("canonical_name") or "相关产品")
    summary = dict(report.get("executive_summary", {}))
    for key in ("market_state", "cost_signal", "supply_demand_signal", "inventory_signal", "conclusion"):
        summary[key] = plain_language(summary.get(key), product_name)
    report["executive_summary"] = summary
    material = dict(report.get("material_stage", {}))
    material["cost_outlook"] = plain_language(material.get("cost_outlook"), f"{product_name}制造成本")
    report["material_stage"] = material
    market = dict(report.get("market_stage", {}))
    balance = dict(market.get("supply_demand", {}))
    for key in ("judgement", "method"):
        balance[key] = plain_language(balance.get(key), product_name)
    market["supply_demand"] = balance
    cycle = dict(market.get("inventory_cycle", {}))
    for key in ("stage", "note"):
        cycle[key] = plain_language(cycle.get(key), f"{product_name}供应")
    market["inventory_cycle"] = cycle
    report["market_stage"] = market
    report["drivers"] = [
        {**item, "direction": plain_language(item.get("direction"), product_name), "statement": plain_language(item.get("statement"), product_name)}
        for item in report.get("drivers", [])
    ]
    return report
REQUIRED_TOP_LEVEL = {
    "schema_version",
    "workflow",
    "title",
    "as_of",
    "status",
    "product",
    "executive_summary",
    "material_stage",
    "market_stage",
    "trends",
    "drivers",
    "data_gaps",
    "evidence",
}
CONFIRMATION_BASES = {"user_choice", "explicit_user_confirmation", "cached_user_choice"}


def load_report(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        report = json.load(handle)
    if not isinstance(report, dict):
        raise ValueError("Report must be a JSON object")
    missing = sorted(REQUIRED_TOP_LEVEL - report.keys())
    if missing:
        raise ValueError(f"Report is missing fixed-schema fields: {', '.join(missing)}")
    if report.get("schema_version") != "2.0":
        raise ValueError("schema_version must be 2.0")
    if report.get("workflow") != "full_pipeline":
        raise ValueError("HTML reports require workflow=full_pipeline")
    for field in ("title", "as_of"):
        if not isinstance(report.get(field), str) or not report[field]:
            raise ValueError(f"Report requires non-empty {field}")
    for field in ("trends", "drivers", "evidence", "data_gaps"):
        if not isinstance(report[field], list):
            raise ValueError(f"{field} must be a list")
    for field in ("product", "executive_summary", "material_stage", "market_stage"):
        if not isinstance(report[field], dict):
            raise ValueError(f"{field} must be an object")
    product = report["product"]
    if product.get("classification_confirmation") not in CONFIRMATION_BASES:
        raise ValueError("product.classification_confirmation must prove user confirmation")
    if not isinstance(product.get("subcategory_path"), list) or not product["subcategory_path"]:
        raise ValueError("product.subcategory_path must be a non-empty list")
    material_stage = report["material_stage"]
    for field in ("bom", "prices"):
        if not isinstance(material_stage.get(field), list):
            raise ValueError(f"material_stage.{field} must be a list")
    market_stage = report["market_stage"]
    for field in ("product_prices", "supply_metrics", "demand_metrics"):
        if not isinstance(market_stage.get(field), list):
            raise ValueError(f"market_stage.{field} must be a list")
    for field in ("supply_demand", "inventory_cycle"):
        if not isinstance(market_stage.get(field), dict):
            raise ValueError(f"market_stage.{field} must be an object")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "assets" / "dashboard-template.html",
    )
    args = parser.parse_args()

    report = plain_report(load_report(args.input))
    template = args.template.read_text(encoding="utf-8")
    if template.count(MARKER) != 1:
        raise ValueError(f"Template must contain {MARKER} exactly once")
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace(MARKER, payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(html)
    print(json.dumps({"saved": str(args.output), "workflow": report["workflow"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
