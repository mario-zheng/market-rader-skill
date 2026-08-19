---
name: market-radar
description: 研究产品的当前原材料价格、产品市场价格、供需格局和库存周期，并生成一个合并的、可追溯的中文 HTML 数据面板。用于“某产品当前原材料价格”“某产品成本端有什么变化”“某产品当前市场行情”“某产品供需是否过剩”“库存处于什么周期”等请求。所有请求统一先完成原材料价格阶段，再完成产品市场供需阶段，复用已确认的分类、规格、BOM 和历史观测。
---

# 市场雷达

将产品研究执行为一条固定工作流，并把稳定知识、两类当期观测、综合报告和运行状态永久保存。不要把聊天记忆当作缓存。原材料价格阶段和产品市场阶段仍分别保存数据，但一次运行必须串流执行两个阶段，最后只生成一个合并判断和一个 HTML 面板。

## 0. 总体执行流程

1. 读取 [references/00-runtime/00-data-contract.md](references/00-runtime/00-data-contract.md) 并确定数据目录。运行数据默认使用本 skill 根目录下的 `data/`；知识库固定使用本 skill 根目录下的 `knowledge/`，直接放置 Markdown 文件，不再询问知识库位置。
2. 调用 `python scripts/state_store.py find-profile --data-dir <目录> --product <用户产品>` 查找已确认档案。存在匹配档案时，先向用户展示产品名、细分路径和规格，并只询问“是否为这个已记录产品”。保存 `resume_step=confirm_saved_profile` 后结束本轮；用户确认后复用该档案的分类、规格和已确认 BOM，跳过重复确认，直接进入第 2.3 节。用户否认时才执行第 1.1 节。若档案缺少 BOM 或其他必要确认，只跳过已有确认项并补问缺失项。
3. 不根据用户措辞选择阶段。无论用户问“价格”“行情”“原材料”还是“供需”，都创建或恢复一次 `full_pipeline` 运行，按“产品细分交互关卡 → 规格确认 → BOM 来源确认 → 阶段 1 → 阶段 2 → 综合输出”顺序执行。用户措辞只决定最终摘要的重点。
4. 创建或恢复运行记录。每次向用户提问前保存 `pending_question` 和 `resume_step`；用户补充后从该步骤继续。阶段 1 被关键错误阻塞时暂停阶段 2；阶段 1 仅部分材料缺少数据时可标记 `partial` 并继续阶段 2。

### 0.1 用户沟通规则

- 不向用户透露 workflow、阶段、关卡、缓存键、脚本命令或内部状态名；只说明需要用户选择或补充什么。
- 每轮最多提出一个问题。问题前先用一句话说明目的，随后使用清晰的选项或输入格式。
- 选择题使用短格式，例如：`请选择：1. 工业异步电机  2. 新能源驱动电机  3. 其他（请填写）`。
- 是/否问题使用短格式，例如：`请回答：是 / 否`。用户回答后再提出下一项，不要一次列出多个待办问题。
- 确认时只复述关键对象和变化，不重复整段研究方法。缺数据时直接说明“暂未找到可靠数据”以及需要用户补充的字段。

## 1. 产品识别与确认

两个阶段共用以下产品解析步骤。为保留细分能力，在正式采集前完成产品细分、必要的更小细分和规格确认；不要把产品细分与型号规格混为一谈。

### 1.1 历史产品确认与产品细分

1. 从用户问题中提取核心产品名后传给 `find-profile`。如果返回一个相似档案，只询问：`这是之前记录的“<产品名 / 细分路径 / 规格>”吗？请回答：是 / 否。`如果返回多个档案，列出简短清单并询问：`请选择：序号，或 0. 都不是。`不得在用户确认前使用历史档案的数据作为本次产品口径。
2. 用户确认历史档案后，保存本次 `cached_user_choice`，直接复用该档案的 `product_id`、分类、规格、BOM 和稳定研究结论；只重新采集会随时间变化的价格、供需、库存和成交数据。
3. 用户回答“都不是”或没有匹配档案时，按以下产品细分流程执行。

4. 把“电机”“锂电池”“塑料”“钢材”等仍可分成多个独立 BOM、价格或供需口径的名称判定为上位产品，绝不能直接当作最终细分。
5. 无可复用档案时读取 [references/01-product-confirmation/01-product-classification.md](references/01-product-confirmation/01-product-classification.md)，检索知识库和联网资料后输出候选表。表格固定包含“序号、细分品类、介绍、代表公司、应用领域”。
6. 表格后只提出一个明确问题：“请选择：序号，或输入其他细分品类。”将运行状态保存为 `waiting_user`，`resume_step` 保存为 `confirm_subcategory`，然后**立即结束本轮回答**。不要在同一轮自行选择，不要继续规格、BOM、价格或供需研究。
7. 用户下一条消息选择后，复述选择并询问是否还需更小的产品细分。回答“是”则在已选节点下重新输出下一层候选并再次停止；回答“否”或用户明确给出叶子品类后，保存 `classification.status=confirmed`、`confirmation_basis` 和完整 `subcategory_path`。
8. 接受用户提供的列表外细分并规范化保存。只有 `state_store.py classification-gate` 返回 `gate_open: true` 才能进入规格确认。

即使用户初始输入看起来已经很具体，只要缓存中没有该完整细分的用户确认记录，也要至少复述识别结果并请求一次确认。存在用户已确认且用户再次确认的历史档案时，可以复用，不再重复询问。不得用模型自己的判断代替用户确认。

### 1.2 规格确认

阶段 1 默认执行此步骤；阶段 2 若采用的价格或统计口径依赖不同规格，也复用该规格结果，不重新询问。

- 用户输入已含明确规格，或已确认缓存存在时，直接继续。
- 询问是否需要区分规格。用户需要但不知道时，读取 [references/01-product-confirmation/01-specification-resolution.md](references/01-product-confirmation/01-specification-resolution.md) 研究候选规格并供选择。
- 接受列表外规格。保存用户确认值、别名、证据和确认时间。

## 2. 工作流 1：原材料价格

1. **确认 BOM 来源（首次不可跳过）**：历史档案确认且 `bom.status=confirmed` 时直接复用 BOM，不重复询问。如果用户在本轮附带了新的具体 BOM，也要复述识别结果并确认“使用这个 BOM”。如果没有可复用 BOM，先只询问：“你有当前产品的具体 BOM 吗？请回答：是 / 否。”保存 `status=waiting_user`、`resume_step=confirm_bom_source`，然后立即结束本轮。不得在同一轮自行研究 BOM 或查询价格。
2. 用户回答“是”时，请用户粘贴或上传 BOM；收到后保存原始版本并确认材料范围。用户回答“否”时，读取 [references/02-workflow-1-material-prices/02-bom-resolution.md](references/02-workflow-1-material-prices/02-bom-resolution.md)，研究所选细分与规格的上游材料/核心部件，输出作用、占比口径、占比区间、是否核心和代表供应商，要求用户确认。用户确认后保存 `bom.status=confirmed`。如果已有历史 BOM，回答“否”时可展示并复用历史版本，但必须记录本次选择。
3. **采集价格**：读取 [references/02-workflow-1-material-prices/02-material-price-research.md](references/02-workflow-1-material-prices/02-material-price-research.md)，逐项采集当日或最近交易日价格、单位、地区/市场、规格、涨跌、上月可比值和下月展望。不得混合不可比口径。
4. **保存快照**：将完整观测写入 JSON，再调用 `state_store.py append-snapshot`。同日同口径可更新，跨日观测追加保存。
5. **复用历史并比较**：调用 `state_store.py series` 获取同一材料、规格、地区、币种、计价单位的历史序列；调用 `state_store.py compare` 获取较上周（7 天）和较上月（30 天）的可比值、绝对变化和百分比变化。比较找不到日期容差内的历史值时输出“暂无可比历史数据”，不得再次搜索旧价格。
6. **判断趋势**：至少有 2 个不同日期的同口径有效值时生成趋势序列和 HTML 折线图；只有 1 个日期时保留当前值、较上周/较上月比较结果，并说明历史点数不足。
7. **阶段交接**：保存材料价格阶段结果、历史序列和周/月比较，写入运行状态的 `completed_steps`。不要在此阶段生成最终 HTML；将结果作为阶段 2 和最终综合报告的输入。

## 3. 工作流 2：市场供需与行情

1. **采集供需与库存**：读取 [references/03-workflow-2-market/03-market-data-research.md](references/03-workflow-2-market/03-market-data-research.md)，尽量采集产量、开工率、进口及来源国、出口、厂家库存、社会库存、表观消费量和独立需求代理。所有比较必须对齐月份/周次、地区、单位和口径。
2. **采集产品价格**：读取 [references/03-workflow-2-market/03-product-price-research.md](references/03-workflow-2-market/03-product-price-research.md)，采集主流市场价、区间、涨跌、规格、地区、含税/未税和来源。
3. **判断供需**：只有存在独立于供给恒等式的需求估计时，才计算 `供给 - 需求`。如果需求只有 `产量 + 进口 - 出口` 推导的表观消费量，不得据此宣称短缺或过剩；改用库存变化、开工率、成交/采购、价格等信号形成带置信度的综合判断。
4. **判断库存周期**：读取 [references/03-workflow-2-market/03-inventory-cycle.md](references/03-workflow-2-market/03-inventory-cycle.md)。使用同期需求与库存环比，应用平坦阈值并检查连续期；信号不足时输出“无法判定”或“周期边界”。
5. **复用历史并比较**：追加市场快照；产品价格和需要趋势的市场指标调用 `state_store.py series` 与 `state_store.py compare`，直接从本地历史快照生成趋势、较上周和较上月变化，不重新查询历史日期。
6. **阶段交接**：保存阶段 2 结果、历史序列和周/月比较后进入第 4 节。不要在此处直接输出未经过固定模板渲染的报告。

## 4. 固定格式输出与交付

1. 读取阶段 1 和阶段 2 的全部已保存 JSON，按照 [references/04-output/04-report-schema.md](references/04-output/04-report-schema.md) 构造固定字段的 `full_pipeline` report JSON。
2. 读取 [references/04-output/04-report-template.md](references/04-output/04-report-template.md)，调用 `python scripts/generate_markdown.py --input <report.json> --output <report.md>` 生成固定文字版。
3. 确认 Markdown 生成成功后，再调用 `python scripts/generate_html.py --input <report.json> --output <report.html>` 生成固定 HTML。
4. 调用 `python scripts/generate_delivery.py --markdown <report.md> --html <report.html> --output <delivery.md>` 生成固定最终交付文本。
5. 最终回复必须原样使用 `delivery.md` 的内容，不增加开场白、总结、解释或其他链接；顺序固定为“文字版报告 → HTML 报告”。不得只给 HTML，不得自行增删或重排章节结构。

### 4.1 面向采购与供应链的表达规则

- 面向用户的文字必须使用日常采购和供应链语言，不默认使用金融或证券术语。内部 JSON 字段、脚本参数和标准周期编码可以保留原名，但不得原样暴露为结论。
- 每个判断必须写清影响对象和实际影响。例如“对电机成品价格有上涨推动”“对电机制造成本有增加影响”“对电机交付周期有延长风险”，不得只写“对价格有推动”或“影响较大”。
- 优先使用“某原材料价格上涨/下跌、某产品制造成本增加/减少、供应充足/供应偏紧、库存增加/减少、需求增加/减少、某产品价格较高/较低、短期上下波动”这类表达。
- 禁止单独使用“走强、走弱、利多、利空、承压、拐头、底部、景气、高位震荡、低位震荡、趋势性强”等术语。确需保留标准周期名时，必须在同一句后面补充白话解释。
- 预测必须写成“预计……，原因是……；对采购的影响是……”，不得只写“偏强、偏弱或震荡”。

## 5. 证据与失败规则

- 始终读取 [references/05-evidence-and-failure/05-source-policy.md](references/05-evidence-and-failure/05-source-policy.md)。来源数量不是置信度的充分条件；评价权威性、独立性、时效性、直接性和口径一致性。知识库中的可信行业报告适用单独规则：稳定知识在口径匹配且无冲突时可直接评为高置信度；市场数据在数据所属期满足时效窗口且口径匹配时也可评为高置信度。
- 事实、计算值和预测分开存放。不得把搜索摘要当作最终证据，不得编造实时数据、历史值或预测共识。
- 必需数据缺失时将运行状态保存为 `blocked`，说明失败步骤、已尝试来源、缺失字段和恢复方式，然后停止依赖该数据的计算。非关键指标缺失可标记 `partial` 并继续。
- 用户解决问题后加载运行记录，从 `resume_step` 继续，不重做已确认步骤。
- 输出研究信息，不作投资收益承诺。

## 6. 知识库检索与上下文控制

读取 [references/06-knowledge-retrieval/06-knowledge-retrieval.md](references/06-knowledge-retrieval/06-knowledge-retrieval.md)。知识库固定为 `<skill-root>/knowledge/*.md`，并用于产品分类、规格、BOM、原材料价格、产品价格、供需库存和综合判断。每个研究步骤先检索知识库，再针对缺口联网补充。所有文件平铺存放，不按产品或行业建立子目录。大文件不得整篇读取：先运行 `python scripts/knowledge_index.py` 建立仅含文件名、标题和标题行号的索引，再按关键词选择少量文件，用 `rg -n` 定位命中并分段读取附近内容。证据不足时逐步扩大，不一次性载入整个知识库。

## 7. 资源索引

### 0. 运行基础

- 数据与持久化：[references/00-runtime/00-data-contract.md](references/00-runtime/00-data-contract.md)

### 1. 产品确认

- 产品分类：[references/01-product-confirmation/01-product-classification.md](references/01-product-confirmation/01-product-classification.md)
- 规格确定：[references/01-product-confirmation/01-specification-resolution.md](references/01-product-confirmation/01-specification-resolution.md)

### 2. 工作流 1：原材料价格

- BOM 与原材料构成：[references/02-workflow-1-material-prices/02-bom-resolution.md](references/02-workflow-1-material-prices/02-bom-resolution.md)
- 原材料价格：[references/02-workflow-1-material-prices/02-material-price-research.md](references/02-workflow-1-material-prices/02-material-price-research.md)

### 3. 工作流 2：市场供需

- 供需与库存数据：[references/03-workflow-2-market/03-market-data-research.md](references/03-workflow-2-market/03-market-data-research.md)
- 产品价格：[references/03-workflow-2-market/03-product-price-research.md](references/03-workflow-2-market/03-product-price-research.md)
- 库存周期：[references/03-workflow-2-market/03-inventory-cycle.md](references/03-workflow-2-market/03-inventory-cycle.md)

### 4. 固定输出

- 报告字段：[references/04-output/04-report-schema.md](references/04-output/04-report-schema.md)
- 文字版模板：[references/04-output/04-report-template.md](references/04-output/04-report-template.md)
- 最终交付模板：[references/04-output/04-final-delivery-template.md](references/04-output/04-final-delivery-template.md)

### 5. 证据与失败处理

- 来源与置信度：[references/05-evidence-and-failure/05-source-policy.md](references/05-evidence-and-failure/05-source-policy.md)

### 6. 知识库检索

- 大型知识库检索：[references/06-knowledge-retrieval/06-knowledge-retrieval.md](references/06-knowledge-retrieval/06-knowledge-retrieval.md)

