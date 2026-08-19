# Market Radar

Market Radar 是一个用于产品市场研究的 Codex skill。它围绕用户确认的产品细分、规格和 BOM，查询原材料价格、产品市场价格、供需与库存信息，并保留历史数据用于后续比较。

## 目录结构

```text
market-radar/
├── SKILL.md                    # skill 主流程与调用规则
├── agents/openai.yaml          # skill 展示信息
├── assets/                     # 固定 HTML 仪表板模板
├── example/                    # 示例文件
├── knowledge/                  # UTF-8 Markdown 行业知识库
├── references/                 # 分类规则、数据规则和报告模板
├── scripts/                    # 索引、持久化和报告生成脚本
├── data/                       # 本地运行数据，不提交到 Git
└── README.md
```

## 使用方式

1. 将行业资料转换为 UTF-8 编码的 `.md` 文件，直接放入 `knowledge/`，无需建立子目录。
2. 首次使用或知识库更新后运行：

   ```powershell
   uv run python scripts/knowledge_index.py
   ```

3. 在支持 Codex skill 的环境中调用 `market-radar`，输入产品价格、原材料价格、市场行情或供需分析需求。首次使用会确认产品细分、规格和 BOM；再次询问已记录产品时，可确认后直接复用这些信息并更新时效数据。

## 输出结果

完成分析后会生成固定格式的：

- 中文 Markdown 文字报告
- 自包含 HTML 数据面板
- 原材料和产品价格的历史趋势
- 较上周、较上月的本地历史比较
- 数据来源、置信度和数据缺口

## 效果展示

