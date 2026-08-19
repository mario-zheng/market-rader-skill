##### 王泉⼒ HiClaw Maintainer 阿⾥云云原⽣产品解决⽅案架构师


### **Part 01.** **Part 02.** **Part 03.**


### HiClaw产品定位及架构 HiClaw核⼼能⼒ HiClaw使⽤形态与应⽤场景


### **HiClaw 核心价值点**


### **HiClaw vs OpenClaw**


### **HiClaw 多类型架构演进：从极客桌面到企业级全托管**










### **HiClaw 开源架构**

Manager Agent 编排控制流，Worker

Agent 处理任务流，所有通信（Human 
  - Agent，Agent -> Agent）经由中央

Matrix 服务器并支持端到端加密。

Human可以通过 Matrix 客户端观察。



凭证、密钥、API Key等敏感信息，MCP、

Skill、工具API，LLM统一由AI网关集中管

控。Agent不再持有任何敏感信息，和

LLM、MCP、Skill技能均通过安全身份验

证，确保Agent的可信性。



Manager Agent 创建Agent、监督Agent、

规划任务、分配任务。真正的多Agent模

式，每个Agent独立进程，可配置不同

LLM，不同Skill，职责清晰便于管理。且

Agent实现方可替换。


### **HiClaw 云上企业级架构**




### **HiClaw 在市场格局中的位置**

















本报告来源于三个皮匠报告站（www.sgpjbg.com）,由用户Id:1181721下载,文档Id:1256199,下载日期:2026-05-27


### **HiClaw 多Human，多Agent协作模式**
























### **HiClaw 管控中心——构建企业级Agent统一管控中心**

Woker可信凭证与管理


### **HiClaw LLM 安全统一管理**


### **HiClaw Skill Hub——构建私有化Skill Market**

**HiClaw Skill Hub 提供安全可靠的企业私有Skill Hub** X


支持企业业务Skill注册到Skill Hub
公网Skill经过安全检测以及查验之后注册到Skills Hub




### **HiClaw Agent 引擎自由组合与替换**




### **HiClaw 提供 Claw/Agent Sandbox 运行环境**



**Claw/Agent 需要运行在完全隔离的沙箱环境中**

HiClaw 提供的Sandbox算力具备资源隔离，网络隔离，存储隔离的特性


**Claw/Agent需要和沙箱环境保持Session亲和性**

HiClaw 提供的Sandbox算力具备多种Session亲和的方式



**Claw/Agent是稀疏调用场景，波峰波谷流量方差巨大**

HiClaw 提供的Sandbox算力分钟级可交付万级大规格实例，无需考虑IP分配问题


**每个Claw/Agent动态产生存储路径，且每个路径需要Quota配置**

HiClaw 提供的Sandbox算力支持OSS，NAS，LakeBase动态挂载


### **HiClaw 企业级 Skill/MCP 安全统一管理**








### **HiClaw 企业级 Skill/MCP 安全统一管理Market – Skill、Agent 模板、Team 模板**

**从原子技能到整编团队，双轨底座支撑资产的高效复用与企业级治理**



**Skill 市场**


原子化的技能插件（如 GitHub检

索、日历读取）


**三大核心生态资产：定义数字生产力的新形态**


**Skill 技能共享市场**


Ø 吸收旗下HiMarket项目，打造对标 Skill.sh 的开放技能市场，

开发者可一键发布、订阅和调用标准化的高价值工具链。


**Agent 专家模板库**


Ø 沉淀各行业最佳实践，无需懂代码，业务人员一键克隆“垂直

领域专家”。


**Team 团队建制模板**


Ø 直接打包复用成熟的协同关系。一键拉起一套类似“项目经理

＋ 研发 ＋ 测试”的完整团队。



**Agent 模板**


预装好特定 Prompt 和 Skill

的垂直领域数字员工（如：

前端工程师，数据分析师）



**开源版**



**商业版**



**Team 模板**


包含“Manager +多个协同

Worker"的整编数字团队配置


**双轨技术底座：兼顾开源繁荣与企业安全合规**


**开源版：无缝接入 agency-agents**


Ø 社区驱动，冷启动极快：原生集成主流开源 Agent 库，拥抱庞

大的社区开发者生态。

Ø 开箱即用：降低中小团队与极客玩家的试错门槛，迅速体验多

Agent 协同魅力。


**商业/企业版：基于 Nacos Al Registry 构建**


Ø 企业级 Al 资产治理：将传统的微服务注册发现理念延伸至 Al

时代。

Ø 安全与高可用：提供Agent 泛技能(Prompt、Skill、MCP)的统

一注册、安全管控，满足企业客户的合规与安全要求。


### **HiClaw 提供完善的AI可观测能力**








### **HiClaw 提供完善的 Agent Team 观测舱**


### **HiClaw × AgentLoop** **构建企业级的数字员工“养成”飞轮**

**告别“盲盒式”提示词工程，打造数据驱动的 Agent 持续进化体系**



数据清洗


自动评估



Manager

调度



**理念升级：从“写代码”到科学“养Agent”**

Ø **打破黑盒：** 摒弃拍脑袋写 Prompt 的玄学，依托 HiClaw 沉碇的全量多

Agent 协作上下文，用 **真实业务数据喂养数字员工** 。

Ø **能力爬坡：** 像带应届生一样，让 Worker Agent 在真实的报错和 **人类纠偏**

中学习企业的独有业务逻辑（SOP）。


**无缝对接 AgentLoop 调优引擎**

Ø **数据采集标准化：** HiClaw 负责提供高质量、结构化的多模态协作日志与工

具调用链。

Ø **闭环评估体系：** AgentLoop 负责接入这些数据， **自动化打分** 和 **弱点分析** ，

精准定位是“模型智商不够”、“工具不好用”还是“Prompt 不清晰”。


**企业级的“数据-智能”飞轮（核心链路）**

Ø **发现 (Discover)** ： 监控高频失败的 Task， **沉淀 Bad Case** 。

Ø **对齐 (Align)：** 结合真实用户的打断与重写指令（人类偏好数据），构建企

业 **专属的 DPO/RLHF 训练集** 。

Ø **进化 (Evolve)：** 实现 Prompt 的自动重构，进一步提升效果。


**沉淀企业核心 AI 资产**


Ø **越用越聪明：** 随着业务运行，您基于HiClaw构建的 Agent Team 将从“通

用型 AI”进化为极其契合您公司私有流程的“ **资深专家集群** ”，成为不可

复制的业务壁垒。



Worker

执行





SFT/RLHF



Matrix

协作






### **HiClaw 助力SaaS企业快速AI转型**



























随着Agent时代爆
发，SaaS服务开始
从传统的API/软件
输出形式转向
Agent输出形式，
在HiClaw的支撑下，
让Agent售卖成为
新的范式。
基于HiClaw构建私
有化Skill Hub对外
输出，通过HiClaw
管控中心实现精细
化管控。按需生成
Woker对外提供服
务












### **HiClaw 一人公司和数字员工的三种模式**


### **HiClaw 云上 Agent 云下 Agent 混合使用**


### **千万级商家数字店长落地架构：HiClaw 端云协同方案**

**Manager-Worker 架构赋能商家：智能店铺管理 + 精准运营决策**


### **VibeCoding助手：基于HiClaw的全链路研发“数字外包”**

**IM 一键唤醒，对接 Remote IDE，覆盖"需求-编码-测试-部署"闭环**


### **HiClaw官网 联系方式**


# **Thanks!**


