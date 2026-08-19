# 4.1 固定综合报告 Schema

最终 report JSON 必须使用以下顶层字段，字段名、章节顺序和表格列不可随产品变化。没有可靠数据时使用空数组、`null` 或明确的缺口说明，不删除字段。

```json
{
  "schema_version": "2.0",
  "workflow": "full_pipeline",
  "title": "产品市场雷达",
  "as_of": "YYYY-MM-DD",
  "status": "complete",
  "product": {
    "canonical_name": "",
    "subcategory_path": [],
    "specification": null,
    "region": "中国",
    "classification_confirmation": "user_choice"
  },
  "executive_summary": {
    "market_state": "",
    "cost_signal": "",
    "supply_demand_signal": "",
    "inventory_signal": "",
    "conclusion": ""
  },
  "material_stage": {
    "bom": [],
    "prices": [],
    "cost_outlook": ""
  },
  "market_stage": {
    "product_prices": [],
    "supply_metrics": [],
    "demand_metrics": [],
    "supply_demand": {},
    "inventory_cycle": {}
  },
  "trends": [],
  "drivers": [],
  "data_gaps": [],
  "evidence": []
}
```

## 固定表格字段

- `material_stage.bom[]`：`material`、`role`、`share`、`share_basis`、`core`、`suppliers`。
- `material_stage.prices[]`：`material`、`price`、`unit`、`daily_change`、`weekly_change`、`monthly_change`、`next_month_outlook`、`confidence`、`verification_status`、`as_of`。
- `market_stage.product_prices[]`：`market`、`specification`、`price_type`、`price`、`unit`、`change`、`weekly_change`、`monthly_change`、`as_of`、`confidence`、`verification_status`。
- `market_stage.supply_metrics[]` 与 `demand_metrics[]`：`name`、`value`、`unit`、`period`、`change`、`confidence`。
- `market_stage.supply_demand`：`balance`、`unit`、`judgement`、`method`、`confidence`。
- `market_stage.inventory_cycle`：`demand_change`、`inventory_change`、`threshold`、`stage`、`confidence`、`note`。`stage` 可保存标准周期编码，但最终文字版和 HTML 必须转换为采购人员能理解的说明，并写明对采购的影响。
- `trends[]`：`metric_key`、`label`、`scope_key`、`unit`、`trend_eligible`、`points`；每个点为 `as_of`、`value`。同口径有效点达到 2 个时 `trend_eligible=true`。
- `drivers[]`：`dimension`、`direction`、`statement`、`horizon`、`confidence`。
- `evidence[]`：`evidence_id`、`title`、`publisher`、`url` 或 `path`、`published_date`、`period`、`confidence`。

## 固定页面顺序

1. 标题与数据日期
2. 综合结论
3. 产品与研究口径
4. BOM 与原材料构成
5. 原材料价格
6. 产品市场价格
7. 供给端指标
8. 需求端指标
9. 产品供应与需求对比
10. 产品库存变化阶段
11. 历史趋势
12. 价格、供应和需求变化原因及下月判断
13. 数据缺口
14. 来源与证据

模板必须永久保留这 14 个章节。允许改变的只有标题、文字、数值、表格行数和趋势点；不得让模型自行生成 CSS、HTML 章节或表格列。
