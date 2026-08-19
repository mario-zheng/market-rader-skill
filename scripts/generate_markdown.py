#!/usr/bin/env python3
"""Render the fixed market-radar Markdown report from report JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from generate_html import load_report


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


def plain_language(value: Any, subject: str = "相关产品") -> Any:
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


def plain_report(report: dict[str, Any]) -> dict[str, Any]:
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


def md(value: Any) -> str:
    if value is None or value == "":
        return "暂无可靠数据"
    if isinstance(value, list):
        return "、".join(md(item) for item in value) or "暂无可靠数据"
    return str(value).replace("|", "\\|").replace("\n", " ")


def row(item: dict[str, Any], fields: list[str]) -> str:
    return "| " + " | ".join(md(item.get(field)) for field in fields) + " |"


def rows(items: list[dict[str, Any]], fields: list[str]) -> str:
    return "\n".join(row(item, fields) for item in items) if items else "| 暂无可靠数据 |" + " |" * (len(fields) - 1)


def trend_text(items: list[dict[str, Any]]) -> str:
    eligible = [item for item in items if item.get("trend_eligible") and len(item.get("points", [])) >= 2]
    if not eligible:
        return "暂无可绘制趋势：可比历史数据少于 2 个日期。"
    output = []
    for item in eligible:
        points = item.get("points", [])
        output.append(f"### {md(item.get('label'))}\n\n单位：{md(item.get('unit'))}；口径：{md(item.get('scope_key'))}\n\n| 日期 | 数值 |\n|---|---:|\n")
        output.append("\n".join(row(point, ["as_of", "value"]) for point in points))
        output.append("")
    return "\n".join(output).rstrip()


def render(report: dict[str, Any], template: str) -> str:
    report = plain_report(report)
    product = report["product"]
    summary = report["executive_summary"]
    material = report["material_stage"]
    market = report["market_stage"]
    balance = market["supply_demand"]
    cycle = market["inventory_cycle"]
    evidence = []
    for item in report["evidence"]:
        evidence.append({**item, "source": item.get("url") or item.get("path")})
    replacements = {
        "{{title}}": md(report["title"]),
        "{{as_of}}": md(report["as_of"]),
        "{{status}}": md(report["status"]),
        "{{executive_summary.market_state}}": md(summary.get("market_state")),
        "{{executive_summary.cost_signal}}": md(summary.get("cost_signal")),
        "{{executive_summary.supply_demand_signal}}": md(summary.get("supply_demand_signal")),
        "{{executive_summary.inventory_signal}}": md(summary.get("inventory_signal")),
        "{{executive_summary.conclusion}}": md(summary.get("conclusion")),
        "{{product.canonical_name}}": md(product.get("canonical_name")),
        "{{product.subcategory_path}}": md(product.get("subcategory_path")),
        "{{product.specification}}": md(product.get("specification")),
        "{{product.region}}": md(product.get("region")),
        "{{product.classification_confirmation}}": md(product.get("classification_confirmation")),
        "{{material_stage.bom_table}}": rows(material["bom"], ["material", "role", "share", "share_basis", "core", "suppliers"]),
        "{{material_stage.prices_table}}": rows(material["prices"], ["material", "price", "unit", "daily_change", "weekly_change", "monthly_change", "next_month_outlook", "confidence", "verification_status", "as_of"]),
        "{{material_stage.cost_outlook}}": md(material.get("cost_outlook")),
        "{{market_stage.product_prices_table}}": rows(market["product_prices"], ["market", "specification", "price_type", "price", "unit", "change", "weekly_change", "monthly_change", "as_of", "confidence", "verification_status"]),
        "{{market_stage.supply_metrics_table}}": rows(market["supply_metrics"], ["name", "value", "unit", "period", "change", "confidence"]),
        "{{market_stage.demand_metrics_table}}": rows(market["demand_metrics"], ["name", "value", "unit", "period", "change", "confidence"]),
        "{{market_stage.supply_demand.balance}}": md(balance.get("balance")),
        "{{market_stage.supply_demand.unit}}": md(balance.get("unit")),
        "{{market_stage.supply_demand.judgement}}": md(balance.get("judgement")),
        "{{market_stage.supply_demand.method}}": md(balance.get("method")),
        "{{market_stage.supply_demand.confidence}}": md(balance.get("confidence")),
        "{{market_stage.inventory_cycle.demand_change}}": md(cycle.get("demand_change")),
        "{{market_stage.inventory_cycle.inventory_change}}": md(cycle.get("inventory_change")),
        "{{market_stage.inventory_cycle.threshold}}": md(cycle.get("threshold")),
        "{{market_stage.inventory_cycle.stage}}": md(cycle.get("stage")),
        "{{market_stage.inventory_cycle.confidence}}": md(cycle.get("confidence")),
        "{{market_stage.inventory_cycle.note}}": md(cycle.get("note")),
        "{{trends}}": trend_text(report["trends"]),
        "{{drivers_table}}": rows(report["drivers"], ["dimension", "direction", "statement", "horizon", "confidence"]),
        "{{data_gaps}}": "\n".join(f"- {md(item)}" for item in report["data_gaps"]) or "暂无记录的数据缺口。",
        "{{evidence_table}}": rows(evidence, ["evidence_id", "title", "publisher", "source", "published_date", "period", "confidence"]),
    }
    for marker, value in replacements.items():
        template = template.replace(marker, value)
    if "{{" in template or "}}" in template:
        raise ValueError("Report template contains unreplaced markers")
    return template


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=Path(__file__).resolve().parent.parent / "references" / "04-output" / "04-report-template.md")
    args = parser.parse_args()
    report = load_report(args.input)
    template = args.template.read_text(encoding="utf-8")
    rendered = render(report, template)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)
    print(json.dumps({"saved": str(args.output), "workflow": report["workflow"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
