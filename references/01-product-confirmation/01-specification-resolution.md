# 1.2 规格确定

1. 从用户输入识别牌号、纯度、尺寸、等级、性能、工艺、包装和适用标准等规格信号。
2. 按 [06-knowledge-retrieval.md](../06-knowledge-retrieval/06-knowledge-retrieval.md) 检索所选细分品类的规格章节，再按 [05-source-policy.md](../05-evidence-and-failure/05-source-policy.md) 查公司技术资料、标准和行业资料。
3. 只列出会改变价格、BOM 或统计可比性的关键规格维度。营销名称必须映射到技术参数或标记为厂商专有。
4. 输出表格：`细分品类 | 规格/等级 | 关键参数 | 介绍 | 代表公司 | 应用领域 | 依据`。
5. 接受列表外规格。用户不要求区分规格时保存 `specification = null` 和确认时间，不猜测默认型号。
