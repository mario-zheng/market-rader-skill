## Serverless 技术加速 AI 应用构建

赵庆杰（卢令）Serverless 基础架构团队负责人


2023年12月15日


[目前就职于阿里云云原生][ Serverless ][团队，专注于][ Serverless ][、][PaaS][，分布式系统]
# “ 架构等方向，致力于打造新一代的 Serverless 技术平台，把平台技术做到更加普惠。



架构等方向，致力于打造新一代的 Serverless 技术平台，把平台技术做到更加普惠。
曾就职于百度，负责内部最大的 PaaS 平台，承接了 80% 的在线业务，在 PaaS 方
向，后端分布式系统架构等领域有丰富的经验



赵庆杰
阿里云 Serverless 产品基础架构团队负责人


# ”



www.top100summit.com


#### 01 AI 应用的发展趋势以及面临挑战 02 Serverless 技术加速 AI 应用的构建 03 Serverless AI 成果展示

www.top100summit.com


AI应用稳步增长


www.top100summit.com


### AI 技术概览





AI 应用面临的挑战


 - AI 应用的构建复杂，且需要多环境部署支持，


需要与非 AI 应用集成

 - 随着 AI 应用功能逐渐丰富，调用链路长极大


影响问题的快速发现

 - AI 应用组件无法复用，持续重复造轮子，浪


费资源成本，如绿网能力，队列等

 - 网关通用能力，安全鉴权，限流保护，多协议


支持，防护攻击等


AI 计算力面临的挑战


- GPU 资源紧缺且成本高，需要持续保有购买

- 卡型不统一导致算力不统一，进而影响应用层架


构

- 随着计算规模的提升，容错能力也越来越重要

- 大数据的读取，以及模型的快速加载，对于底层


的技术要求越来越高

















www.top100summit.com


### 经常听到的问题？















www.top100summit.com


www.top100summit.com


### 不同角色，在 AI 场景下的诉求

























如何高效率低成

本落地



如何方便快捷部

署使用





www.top100summit.com


### Serverless 开发平台 AI 场景

函数计算提供构建现代化高可用 AI 应用的简化路径，是 AI 应用的最佳实践



































www.top100summit.com


### Serverless GPU – 按请求计量





www.top100summit.com


### 如何消除冷启动--容器启动加速

















数据流


数据流











www.top100summit.com


### GB 级镜像实例秒级启动























www.top100summit.com


##### 可用区容灾、环境启停、网络规划、网关路由

















































以上数据来源于 阿里云内部业务数据


### 运维、弹性、灰度、流水线

















以上数据来源于 阿里云内部业务数据


##### 无损下线、全链路灰度

微服务无损下线



微服务全链路灰度























































以上数据来源于 阿里云内部业务数据


www.top100summit.com




















### 控制台界面



www.top100summit.com


### 函数计算 AI 开发模式



































www.top100summit.com


www.top100summit.com


##### Serverless 函数计算 GPU 应用场景选型指南（针对推理）











































www.top100summit.com


www.top100summit.com


### AIGC 应用场景



















www.top100summit.com


### Stable Diffusion 与平台集成实践方案















www.top100summit.com


### Serverless WebUI-方案优势解析





















|优势项|社区webui|自建webui|Serverless WebUI|
|---|---|---|---|
|部署方式|台式PC安装，需要3090/4090等桌<br>面级显卡支持，用户自行安装部署<br>webui|购买GPU服务器搭建webui服务，<br>用户自行安装部署webui|一键拉起，预置好标准镜像，即开即用|
|模型、插件管理|开源安装后，git下载到本机，需要<br>用户diy，概率性存在因网速、环境<br>等原因下载插件时卡死|开源安装后，git下载到本机，需要<br>用户diy，概率性存在因网速、环境<br>等原因下载插件时卡死|预置中英双语版本、controlnet、pix2pix等常用插件，<br>模型、插件、输出图片等目录支持挂载为oss共享存储目<br>录，可统一管理和维护，webui服务重启不受影响|
|性能优化|webui原生提供lowvram、xformer<br>等加速方式|ecs提供AIACC加速器|默认支持模型以及镜像加速能力|
|企业级特性|单机版，不具备企业级特性|需要自建调度系统，处理用户与<br>GPU实例之间的对应关系，将用户<br>调度到指定webui服务，但是无法<br>实现在一个webui服务上实现多卡<br>调度|1.<br>多人团队可通过独享 SD 函数，使用互不干扰<br>2.<br>支持单服务多卡集群按使用量弹性伸缩，保证集<br>群使用率<br>3.<br>提供账号体系，支持用户鉴权，按用户身份区分<br>可看到的模型、图片成果<br>4.<br>按请求收费，按使用量收费，毫秒计费|
|特殊辅助插件|跟社区一致|跟社区一致|1.<br>模型及对应的高质量提示词自动关联提示<br>2.<br>基于模型的提示词扩展<br>3.<br>训练/finetune插件，隔离训练/出图使用资源|


www.top100summit.com


### 服饰穿搭实践

www.top100summit.com


### GB 级镜像实例秒级启动















www.top100summit.com


### 大语言模型知识库的基本原理











































www.top100summit.com


### 函数计算产品— 基于云原生大模型智能问答实践

用户身边 0 成本的“高级技术专家”，致力于提升云原生产品使用体验、降低云原生应用生产门槛





www.top100summit.com


### 整体系统架构

云原生大模型践行可扩展架构设计，便于更多的云原生产品因大模型技术而受益





























www.top100summit.com


### 函数创建

利用大模型快速理解用户诉求，匹配合适的触发器设置、生成满足业务诉求的脚手架代码



















www.top100summit.com


### 监控运维

通过云原生大模型对话式唤起现有Serverless监控面板，面向应用整合常见Ops操作











www.top100summit.com


微信官方公众号：壹佰案例
关注查看更多年度实践案例


