# {{title}}

数据截至：{{as_of}}  
报告状态：{{status}}

## 1. 综合结论

- 当前产品市场情况：{{executive_summary.market_state}}
- 原材料及制造成本变化：{{executive_summary.cost_signal}}
- 当前产品供应与需求：{{executive_summary.supply_demand_signal}}
- 当前产品库存变化：{{executive_summary.inventory_signal}}
- 综合结论：{{executive_summary.conclusion}}

## 2. 产品与研究口径

| 项目 | 内容 |
|---|---|
| 产品 | {{product.canonical_name}} |
| 细分路径 | {{product.subcategory_path}} |
| 规格 | {{product.specification}} |
| 地区 | {{product.region}} |
| 分类确认 | {{product.classification_confirmation}} |

## 3. BOM 与原材料构成

| 原材料/部件 | 作用 | 占比 | 占比口径 | 核心 | 代表供应商 |
|---|---|---|---|---|---|
{{material_stage.bom_table}}

## 4. 原材料价格

| 原材料 | 当前价格 | 单位 | 当日涨跌 | 较上周 | 较上月 | 下月预期 | 置信度 | 验证状态 | 日期 |
|---|---:|---|---:|---:|---:|---|---|---|---|
{{material_stage.prices_table}}

未来一个月原材料价格及制造成本判断：{{material_stage.cost_outlook}}

## 5. 产品市场价格

| 市场 | 规格 | 价格类型 | 价格 | 单位 | 当期涨跌 | 较上周 | 较上月 | 日期 | 置信度 | 验证状态 |
|---|---|---|---:|---|---:|---:|---:|---|---|---|
{{market_stage.product_prices_table}}

## 6. 供给端指标

| 指标 | 数值 | 单位 | 所属期 | 变化 | 置信度 |
|---|---:|---|---|---:|---|
{{market_stage.supply_metrics_table}}

## 7. 需求端指标

| 指标 | 数值 | 单位 | 所属期 | 变化 | 置信度 |
|---|---:|---|---|---:|---|
{{market_stage.demand_metrics_table}}

## 8. 产品供应与需求对比

- 供应量减需求量：{{market_stage.supply_demand.balance}} {{market_stage.supply_demand.unit}}
- 当前产品供需判断：{{market_stage.supply_demand.judgement}}
- 计算方法：{{market_stage.supply_demand.method}}
- 置信度：{{market_stage.supply_demand.confidence}}

## 9. 产品库存变化阶段

- 需求环比：{{market_stage.inventory_cycle.demand_change}}
- 库存环比：{{market_stage.inventory_cycle.inventory_change}}
- 平坦阈值：{{market_stage.inventory_cycle.threshold}}
- 库存变化阶段：{{market_stage.inventory_cycle.stage}}
- 置信度：{{market_stage.inventory_cycle.confidence}}
- 库存变化说明及对产品供应的影响：{{market_stage.inventory_cycle.note}}

## 10. 历史趋势

{{trends}}

## 11. 价格、供应和需求变化原因及下月判断

| 维度 | 方向 | 判断 | 期限 | 置信度 |
|---|---|---|---|---|
{{drivers_table}}

## 12. 数据缺口

{{data_gaps}}

## 13. 来源与证据

| ID | 标题 | 机构 | 来源 | 发布日期 | 数据期 | 置信度 |
|---|---|---|---|---|---|---|
{{evidence_table}}

> 本报告由固定模板生成；数据缺失时保留章节并标记“暂无可靠数据”。
