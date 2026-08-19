# 0.1 数据与持久化契约

## 目录

运行脚本会按需创建：

```text
data/
  profiles/                 # 稳定知识与用户确认版本
  observations/<product>/   # 按 workflow 保存的日期快照
  runs/<run-id>/state.json  # 断点与错误
  outputs/<run-id>/         # report.json、report.md、report.html、delivery.md
  knowledge-index.json
```

知识库固定位置为 skill 根目录下的 `knowledge/*.md`，文件平铺存放。`knowledge-index.json` 只保存索引元数据，不复制知识库正文。

不要覆盖已确认历史。档案更新时追加 `revisions`；跨日期观测追加保存。同一日期、同一 workflow 和同一口径再次采集时更新该快照，并保留 `updated_at`。

## 产品档案

必需字段：

```json
{
  "schema_version": "1.0",
  "product_id": "canonical-id",
  "canonical_name": "产品名",
  "aliases": ["别名"],
  "subcategory_path": ["一级", "二级"],
  "specification": null,
  "classification": {
    "status": "confirmed",
    "confirmation_basis": "user_choice",
    "confirmed_value": "磷酸铁锂动力电池",
    "evidence": []
  },
  "bom": {"status": "unknown", "revisions": []},
  "confirmed_at": "ISO-8601"
}
```

`product_id` 由规范名称、完整细分路径和影响口径的规格共同确定。不要仅用用户原句作为 ID。`confirmation_basis` 只能是 `user_choice`、`explicit_user_confirmation` 或 `cached_user_choice`；模型自行判断不算确认。

当 `find-profile` 返回匹配档案时，只有用户明确确认后才能使用 `cached_user_choice` 复用分类、规格和 BOM。档案必须保留 `classification.status=confirmed` 和 `bom.status=confirmed`，否则只复用已确认字段并补问缺失确认。

## 观测快照

必需字段：`schema_version`、`workflow`（`material_prices` 或 `market_balance`）、`product_id`、`as_of`、`scope_key`、`metrics`、`evidence`、`status`、`errors`、`created_at`。每个 metric 应包含 `metric_key`、名称、值/区间、单位、币种、地区、规格、价格类型、所属期和证据 ID。

`scope_key` 是可比口径的稳定字符串。材料价格至少包含材料、规格、地区、币种、单位和价格类型；市场指标至少包含产品、细分、规格、地区、指标定义和频率。

`state_store.py compare` 只比较相同 `product_id`、`workflow`、`metric_key` 和 `scope_key` 的历史值。默认比较 7 天和 30 天，分别允许最多 3 天和 7 天的日期偏差；没有可比值时返回 `no_comparable_history`，不得跨口径或跨产品补值。

## 运行状态

必需字段：`run_id`、`workflow`、`product_query`、`product_id`（可为空）、`status`（`in_progress|waiting_user|partial|blocked|complete`）、`completed_steps`、`resume_step`、`pending_question`、`missing_inputs`、`errors` 和时间戳。询问是否复用历史档案时保存 `resume_step=confirm_saved_profile`；输出分类候选后保存 `resume_step=confirm_subcategory`。两种情况都必须保存 `status=waiting_user` 并停止该轮。

## HTML report JSON

最终报告的完整字段和固定章节见 [04-report-schema.md](../04-output/04-report-schema.md)。文字版章节和占位符见 [04-report-template.md](../04-output/04-report-template.md)。两个阶段的快照仍分别使用 `material_prices` 和 `market_balance`；最终合并报告使用 `full_pipeline`。最终必须同时生成 `report.md`、`report.html` 和 `delivery.md`：先 Markdown、后 HTML，再用固定交付模板包装。两个报告文件都只能展示输入 JSON 中存在的数据，缺失字段由生成器拒绝，空数据由模板显示为“暂无可靠数据”。最终聊天回复必须原样采用 `delivery.md`。
