# Information Router Plugin：产品与实施计划

版本：0.1-draft  
目标仓库：`lkh-cq/information-router`  
插件名：`information-router`  
核心 Skill：`route-information`

## 1. 决策摘要

本项目不继续修补一份“固定数据库 + 固定检索式”的模板，而是建立一个通用的信息路由范式：Agent 先识别任务、风险、时效、证据关系和输出契约，再自主选择检索通道、查询块、证据结构与停止条件。

首版采用 **skills-only 插件**，不引入 MCP 服务。这样可以先验证路由判断是否可靠，而不把部署、鉴权和持久化复杂度混进方法学验证。只有当“跨会话证据账本、受控外部系统访问、确定性路由服务”成为真实需求时，才升级为 Skill + MCP。

新插件必须完全独立：

- 不位于 `sanyuan` 或 `sanyuan-context-router` 仓库；
- 不依赖三元三才、意识总线、ρ/θ、藏归、元信息空间等术语或运行时；
- 不引用三元仓库中的代码、schema、状态节点或私有约定；
- 使用独立的概念模型、版本历史、测试集与发布流程；
- 允许未来通过标准输入/输出与其他插件组合，但不建立反向依赖。

## 2. 现有检索范式缺失的维度

原范式的主要问题不是“数据库还不够多”，而是把信息检索压缩成了“大论文优先的文献筛选”。这会同时造成召回偏倚、结构偏倚和解释偏倚。

| 缺失维度 | 典型缺口 | 造成的偏倚 | 新范式的处理 |
|---|---|---|---|
| 任务意图 | 把查事实、找全证据、验证争议、机制追踪、复现都当成一种检索 | 输出与真实任务错配 | 先分类 `lookup / discover / verify / synthesize / reproduce / monitor` |
| 证据粒度 | 综述、指南、大样本优先，小研究默认降权或消失 | 长尾与新颖发现被系统性漏检 | 检索阶段不以研究规模淘汰；评价阶段再标注强度与局限 |
| 关系与拓扑 | 只搜主题共现，不搜上游、下游、并行、旁通、代偿、拮抗、脱靶 | “已有通路”和“旁通路”不可见 | 独立启用 topology lane，并显式记录关系类型 |
| 证据极性 | 偏向阳性和支持性结果 | 发表偏倚、确认偏倚 | 独立检索 null、negative、contradictory、withdrawn、corrected |
| 术语时间轴 | 只用当前术语 | 老论文、旧命名、同义词、缩写被漏检 | 建立别名、历史名称、拼写和命名迁移查询块 |
| 来源生态 | 过度集中于主流期刊和大数据库 | 灰色文献、会议、学位论文、注册记录、代码和数据缺失 | 按任务选择 source classes，不使用固定数据库清单 |
| 文献身份 | 把一项研究的预印本、摘要、正式论文、勘误当作独立证据 | 重复计权和证据膨胀 | 以 study family、版本链和数据重叠去重 |
| 情境条件 | 对物种、组织、剂量、时间窗、平台、地区等记录不足 | 错误外推 | EvidenceRecord 强制保留 context 与适用边界 |
| 方法与资源 | 只提结论，不追数据、代码、协议、试剂、数据库记录 | 无法复现或验证 | resource lane 定向追踪数据、代码、protocol 和 registry |
| 时效与版本 | 没有 freshness、更新日期、撤稿和替代版本策略 | 当前事实与历史事实混用 | 任务画像记录时效，输出标注检索日期与版本状态 |
| 偏倚结构 | 只评价单篇研究质量 | 不识别来源、语言、排名、可得性和算法偏倚 | BiasLedger 对整个检索过程做补偿与残余风险记录 |
| 停止规则 | 依赖条数、主观饱和或固定数据库完成 | 过早停止或无限检索 | 使用哨兵召回、边际增益、覆盖缺口与未决矛盾联合停止 |
| 可追溯性 | 查询、筛选、归并、判断之间没有稳定映射 | 无法审计或重跑 | RoutePlan → QueryBlock → EvidenceRecord → Claim 的链式溯源 |

核心纠偏原则是：**相关性、证据强度和决策权重必须分开。** 小论文可以高相关但低确定性；大论文可以高确定性但与具体机制关系较远。路由器不得用单一“质量分”提前抹去这种差异。

## 3. 产品边界

### 3.1 插件负责什么

1. 将自然语言请求编译为 `RequestProfile`。
2. 选择最小充分的检索通道集合。
3. 把复杂主题拆成可独立执行的查询块，而不是把所有维度强行 AND。
4. 指导 Agent 使用当前可用的网页、GitHub、本地文件、学术数据库或连接器。
5. 将结果规范化为证据记录、关系边和偏倚账本。
6. 提供可解释的停止条件和输出契约。

### 3.2 插件不负责什么

- 不自称通用搜索引擎或事实数据库；
- 不绕过付费墙、权限、robots、许可或用户禁止使用的来源；
- 不把搜索排名、期刊名气或引用数当作真实性代理；
- 不在缺少工具或原文时捏造执行结果；
- 不强制简单问题运行完整工作流；
- 不用一个综合分数替代证据分维度判断；
- 不在首版保存敏感或长期用户数据。

## 4. 通用路由模型

### 4.1 RequestProfile

任务画像至少包含：

- `goal`：用户真正要完成的决定或产物；
- `mode`：查找、发现、验证、综合、复现或监测；
- `domain`：领域及其专门来源；
- `stakes`：低、中、高风险；
- `freshness`：历史、截至某日、当前或持续更新；
- `modalities`：网页、论文、代码、数据、标准、专利等；
- `constraints`：语言、地区、年代、开放获取、禁止来源等；
- `must_preserve`：不得在重构中丢失的实体、关系和条件；
- `output_contract`：答案、证据表、检索式、审计记录或可复现包。

### 4.2 检索通道（lanes）

| 通道 | 何时启用 | 主要目标 |
|---|---|---|
| orientation | 术语含糊、领域陌生或问题边界未定 | 建立实体、术语和来源地图 |
| direct | 几乎所有非平凡任务 | 直接回答核心问题 |
| alias | 存在旧名、缩写、命名漂移或跨学科术语 | 扩展同义和历史名称 |
| topology | 涉及机制、过程、因果、依赖关系 | 上下游、并行、旁通、代偿、拮抗、反馈、脱靶 |
| contradiction | 验证主张、高风险决策或证据冲突 | 反例、阴性、失败复现、勘误、撤稿 |
| long-tail | 主题新、稀疏、小众或用户要求小论文 | 小样本、短文、会议、预印本、学位论文、灰色文献 |
| resource | 需要复现、实现或资源定位 | 数据、代码、协议、注册记录、标准、试剂 |
| citation | 已有种子材料或领域核心论文 | 前向、后向及相似文献扩展 |

不是每次都启用全部通道。路由器必须说明每个已选通道的触发理由，并给未选高价值通道留下可见的残余风险。

### 4.3 查询维度

建议采用七维描述，但不要求在单个检索式中同时出现：

- `E` Entity：实体、对象、人群、技术、疾病、组件；
- `C` Context：物种、组织、环境、剂量、时间、地区、版本；
- `R` Relation：激活、抑制、依赖、调节、替代、矛盾、关联；
- `P` Path/Process：机制、通路、流程、上下游和旁通；
- `S` Source：论文、网页、代码、数据、专利、标准、注册记录；
- `T` Time：发表、事件、更新、版本与撤回时间；
- `V` Viewpoint：支持、反对、阴性、边界、失败和不确定性。

执行时应生成多个 QueryBlock，例如 `E+C`、`E+R`、`E+P+V`、`E+S`，而不是把七维全部 AND 后得到一个精确但低召回的查询。

## 5. 独立数据模型

插件使用以下中性对象，不继承任何三元仓库模型：

- `RequestProfile`：任务与约束；
- `RoutePlan`：通道、顺序、并行组、来源和停止规则；
- `QueryBlock`：可执行查询单元及其目标；
- `EvidenceRecord`：证据、上下文、方法、版本和来源；
- `RelationEdge`：源实体—关系—目标实体及限定条件；
- `BiasLedger`：偏倚信号、补偿动作和残余风险；
- `StopReport`：停止依据、未覆盖项和下一轮入口；
- `AcademicProtocol`：不可漂移的 `Target`、版本化 `Theme` 与 `sub_n` 拓扑、三轮 Loop、逐轮对齐/清洗/审核/回归门、可审计证据链。

## 6. 版本路线图

| 阶段 | 产物 | 验收条件 |
|---|---|---|
| M0 范式冻结 | 术语表、边界、对象模型、路由规则 | 不含三元依赖；同一案例可被两位评审解释一致 |
| M1 skills-only MVP | manifest、`route-information`、四份 references | 能处理简单、复杂、机制、长尾、反证五类请求 |
| M2 确定性校验 | JSON Schema、静态校验脚本、示例输出 | 缺字段、非法 lane、无 provenance 能被明确拒绝 |
| M2.5 学术协议 | `academic-protocol.schema.json`、`validate_academic.py`、`eval_runner.py` | Target 哈希不可漂移；Theme `sub_n` 拓扑无环；三轮 Loop 顺序严格；locator 真实；对抗样例全部被拒 |
| M3 系统评测 | 20–30 个正/负/边界案例与评分规则 | 触发准确；无证据伪造；关键通道召回达标 |
| M4 本地插件测试 | 本地 marketplace 安装与 ChatGPT/Codex 测试 | direct、indirect、follow-up、negative、boundary 均通过 |
| M5 MCP 决策门 | ADR：继续 skills-only 或增加 MCP | 只有真实的持久化、鉴权或受控服务需求才进入 MCP |
| M6 发布 | 独立 GitHub 仓库、版本、变更日志、发布说明 | 不引用三元仓库；安装、卸载、回滚和许可证清晰 |

## 7. 评测设计

### 7.1 必测场景

1. 一个一句话、可直接回答的问题：不得过度路由。
2. 一个生物医学旁通路问题：必须启用 topology 与 contradiction。
3. 一个冷门机制问题：必须覆盖小论文、旧术语和灰色来源。
4. 一个 GitHub 软件问题：必须路由到代码、issue、release 与官方文档。
5. 一个当前法规或高风险问题：必须要求时效和权威来源。
6. 一个已有种子论文的扩展问题：必须执行引文链和版本归并。
7. 一个要求复现的任务：必须搜代码、数据、协议和依赖版本。
8. 一个用户明确禁止网页搜索的任务：必须降级而非越权。
9. 一个完全无关的请求：Skill 不应隐式触发。
10. 一个工具缺失场景：只能交付计划和缺口，不能声称已经检索。

### 7.2 指标

- 触发精确率与召回率；
- 关键通道覆盖率；
- 哨兵材料召回率；
- 来源与版本溯源完整率；
- 矛盾保留率；
- 小/负/非主流证据保留率；
- 无依据断言数（目标为 0）；
- 工具调用经济性；
- 简单任务的过度规划率；
- 评审者间对 RoutePlan 的一致性。

不建议把以上指标压缩成一个总分；使用分维度阈值和硬失败条件更可审计。

## 8. 停止策略

停止不是“搜到 N 篇”或“数据库都跑完”。建议同时满足：

1. 核心问题及所有 must-preserve 项均有对应查询块；
2. 预先设定的哨兵材料可以被召回；
3. 最近一轮新增独立证据或新关系的边际收益低于阈值；
4. 高价值通道不存在未解释的空白；
5. 关键矛盾已解析，或已作为未决问题显式保留；
6. 来源、版本、检索日期和限制可被复查。

高风险任务不得仅因边际收益降低就停止；仍需满足权威来源与矛盾检查。

## 9. GitHub 实施策略

独立仓库 `lkh-cq/information-router` 已建立。本项目将直接发布到该仓库，不写入或复用任何三元仓库。建议按以下顺序推进：

1. 创建独立仓库并明确 public/private 与许可证；
2. 将 scaffold 作为初始提交推送至 `main`；
3. 用 `feat/router-mvp` 分支实现 M1；
4. 用 issue 分别追踪 schema、eval、MCP decision；
5. 首个 PR 只交付 skills-only MVP 和评测基线；
6. 通过本地 marketplace 测试后打 `v0.1.0` 标签。

不要复用空的 `Notepress-pro`，也不要在 `sanyuan` 或 `sanyuan-context-router` 中创建子目录，以免所有权、版本史和术语边界再次耦合。

## 10. 风险登记

| 风险 | 早期信号 | 缓解措施 |
|---|---|---|
| 通用化过度 | 所有任务都生成同样的完整流程 | 最小充分路由；简单问题设快速路径 |
| 伪自主 | 只把固定数据库清单换成新术语 | lane 选择必须依赖 RequestProfile 与工具能力 |
| 长尾噪声 | 小论文召回增加但无法判断独立性 | 版本归并、方法与情境字段、证据强度后置评价 |
| 关系幻觉 | Agent 从共现推断机制边 | RelationEdge 必须区分 reported、inferred、hypothesized |
| 来源偏倚隐藏 | 只展示最终答案 | 强制输出 BiasLedger 与未覆盖通道 |
| MCP 过早 | 大量时间花在服务部署而非路由质量 | M5 决策门；v0.1 固定 skills-only |
| Skill 误触发 | 普通问答被完整工作流淹没 | description 与负例评测；提供 fast path |
| 领域适配污染核心 | 生物医学规则变成全局规则 | 核心中性；领域规则放 adapter/reference |

## 11. 参考基线

插件工程遵循 OpenAI 的官方插件与 Skill 结构：

- [Build plugins](https://learn.chatgpt.com/docs/build-plugins)
- [Build skills](https://learn.chatgpt.com/docs/build-skills)
- [Plugin architecture](https://developers.openai.com/plugins/concepts/plugins)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
- [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)

检索与报告方法可借鉴但不机械套用：

- [Cochrane Handbook, Chapter 4: Searching for and selecting studies](https://www.cochrane.org/authors/handbooks-and-manuals/handbook/current/chapter-04)
- [PRISMA-S reporting guideline](https://systematicreviewsjournal.biomedcentral.com/articles/10.1186/s13643-020-01542-z)
- [PRESS search strategy peer review](https://www.cda-amc.ca/press-peer-review-electronic-search-strategies)
- [TARCiS terminology](https://ub.unibas.ch/de/ub-medizin/tarcis/)

这些标准提供检索透明度、同行评审和报告基线，但本插件的目标更广：它同时覆盖网页、代码、数据、通路关系、长尾材料和非系统综述型信息任务。
