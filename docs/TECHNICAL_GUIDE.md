# Information Router Plugin：技术指导

本文档给出可直接实现的 v0.1 技术方案。它面向独立仓库 `information-router`，不要求或引用任何三元仓库组件。

## 1. 技术选择

### 1.1 v0.1 使用 skills-only

官方插件架构允许插件只包含 Skill。对信息路由而言，首要不确定性是“Agent 能否可靠分类任务并选择通道”，不是服务端吞吐、鉴权或存储。因此 v0.1 只包含：

- `.codex-plugin/plugin.json`；
- `skills/route-information/SKILL.md`；
- Skill 的 `references/` 与 `agents/openai.yaml`；
- 仓库级 schema 和 eval；
- 可选的纯本地确定性校验脚本。

### 1.2 MCP 的引入条件

仅在至少一项成立时引入 MCP：

1. RoutePlan 或 EvidenceRecord 需要跨会话持久化；
2. 必须访问带鉴权的专用数据库或企业系统；
3. 需要服务端强制 schema、去重或权限策略；
4. 多 Agent 必须共享同一个证据账本；
5. 本地脚本无法提供所需的确定性与审计性。

若只是指导 Agent 使用网页、GitHub、本地文件或已有工具，不需要 MCP。

## 2. 推荐仓库结构

```text
information-router/
├── .codex-plugin/
│   └── plugin.json
├── skills/
│   └── route-information/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       └── references/
│           ├── routing-model.md
│           ├── source-policy.md
│           ├── evidence-and-bias.md
│           └── output-contracts.md
├── schemas/
│   ├── route-plan.schema.json
│   └── evidence-record.schema.json
├── evals/
│   ├── cases.jsonl
│   └── rubric.md
├── scripts/
│   ├── validate_route.py
│   └── validate_evidence.py
├── docs/
│   ├── PLAN.md
│   └── TECHNICAL_GUIDE.md
└── README.md
```

`SKILL.md` 只保留决策流程和资源路由。长篇枚举放入 `references/`，schema、测试和开发文档放在 Skill 目录外，避免每次触发都加载无关内容。

## 3. 插件 manifest

`.codex-plugin/plugin.json` 的首版建议为：

```json
{
  "name": "information-router",
  "version": "0.1.0",
  "description": "Route complex information requests into reproducible search, relation expansion, long-tail discovery, contradiction checks, and bias audits.",
  "skills": "./skills/"
}
```

首版不声明 MCP。manifest 中的版本与 Git tag 保持一致。

## 4. Skill 元数据

`SKILL.md` frontmatter：

```yaml
---
name: route-information
description: Route complex research and information requests across web, literature, code, data, relation-topology, contradiction, long-tail, and provenance channels. Use when the user asks for a comprehensive or reproducible search, evidence mapping, source routing, pathway or dependency expansion, small-study discovery, bias auditing, or when a task spans multiple source types and must preserve traceability. Do not use for a simple one-step fact lookup unless the user explicitly asks for the routing process.
---
```

关键点：

- `name` 使用动词短语且与目录名一致；
- `description` 同时描述能力、触发场景和负边界；
- 不把工具名写成硬依赖；
- 简单查事实保留 fast path，防止误触发后过度展开。

`agents/openai.yaml`：

```yaml
interface:
  display_name: "Information Router"
  short_description: "Route complex searches with traceable evidence"
  brand_color: "#2563EB"
  default_prompt: "Use $route-information to turn this request into a traceable multi-source search and evidence plan."

policy:
  allow_implicit_invocation: true
```

首版不声明 `dependencies.tools`，因为路由器必须对可用工具做能力降级，而非要求所有环境都有同一个 MCP。

## 5. Agent 执行算法

### 5.1 总流程

```text
request
  → compile RequestProfile
  → choose minimal lanes
  → create QueryBlocks and SourcePlan
  → execute with available capabilities
  → normalize and deduplicate evidence
  → expand or challenge relations
  → audit bias and coverage
  → test stop rules
  → render the requested output contract
```

### 5.2 伪代码

```python
def route_information(request, capabilities):
    profile = compile_request_profile(request)

    if profile.is_simple and not profile.requires_process:
        return run_fast_path(profile, capabilities)

    lanes = choose_minimal_lanes(profile)
    blocks = compile_query_blocks(profile, lanes)
    sources = choose_sources(profile, lanes, capabilities)

    raw = execute(blocks, sources, capabilities)
    records = normalize(raw)
    records = merge_versions_and_study_families(records)
    edges = extract_relations(records, label_inference=True)
    bias = audit_bias(profile, blocks, sources, records)

    while not stop_rules_met(profile, records, edges, bias):
        next_blocks = target_gaps_and_contradictions(profile, records, edges, bias)
        if not next_blocks:
            break
        raw += execute(next_blocks, sources, capabilities)
        records = normalize_and_merge(raw)
        edges = extract_relations(records, label_inference=True)
        bias = audit_bias(profile, blocks + next_blocks, sources, records)

    return render_output(profile, records, edges, bias)
```

这是行为规范，不要求实现为单个 Python 函数。Skill 可直接指导 Agent 执行；脚本只承担 schema 与确定性检查。

## 6. 路由规则

### 6.1 任务模式判定

| 模式 | 判定信号 | 默认输出 |
|---|---|---|
| lookup | 单一事实、范围窄、无需全面性 | 简短答案 + 权威来源 |
| discover | 不知道有什么、寻找新方向 | 主题地图 + 候选集 + 缺口 |
| verify | 验证主张、争议或高风险判断 | 支持/反对证据 + 结论边界 |
| synthesize | 需要全景、比较或综述 | 证据矩阵 + 综合结论 |
| reproduce | 复现实验、分析或软件行为 | 材料链、步骤、版本、阻塞项 |
| monitor | 未来变化会改变决定 | 基线、变化信号与监测条件 |

### 6.2 lane 选择函数

- `direct`：所有非平凡任务；
- `orientation`：未知术语、多义词、跨领域或用户目标不清；
- `alias`：命名历史长、旧论文重要、实体有多种 identifier；
- `topology`：请求出现机制、通路、依赖、原因、替代、旁通、代偿、上下游；
- `contradiction`：verify、高风险、结论性语言、已知争议；
- `long-tail`：稀疏主题、前沿主题、小论文、灰色文献或发表偏倚风险；
- `resource`：reproduce、实现、数据、代码、协议、标准；
- `citation`：用户给出种子论文、专利、仓库、issue 或标准。

选择结果必须是“最小充分集合”。每个 lane 记录：触发信号、目标、查询块、来源类、完成条件、残余风险。

## 7. QueryBlock 设计

建议对象：

```json
{
  "id": "QB-004",
  "lane": "topology",
  "objective": "Find reported bypass or compensatory routes around target X",
  "concepts": {
    "entity": ["X", "alias-X"],
    "relation": ["bypass", "compensatory", "redundant", "feedback"],
    "context": ["human", "cell type Y"]
  },
  "source_classes": ["primary-literature", "pathway-database"],
  "must_preserve": ["cell type Y"],
  "status": "planned"
}
```

编译规则：

1. 一个 QueryBlock 只服务一个可判定目标；
2. 保留 must-preserve 条件，但不要把所有维度塞入每条检索式；
3. 不同来源使用不同语法适配，核心对象不保存平台专用语法；
4. broad → focused → relation expansion → challenge 的轮次可追踪；
5. 所有新增查询必须指向覆盖缺口、矛盾或新发现的实体/关系。

## 8. SourcePlan 与能力降级

路由器按来源类别工作，而不是写死数据库名称：

- authoritative web：政府、标准组织、官方产品/项目文档；
- scholarly index：综合或领域数据库；
- primary repositories：论文、预印本、注册、学位和会议；
- relation resources：通路、相互作用、知识图谱；
- code ecosystem：仓库、issue、commit、release、包注册表；
- data ecosystem：数据仓库、补充材料、protocol；
- citation graph：前向、后向和相似条目；
- local/user material：附件、已有笔记和用户给出的种子集。

执行政策：

- 当前事实、价格、法规、软件版本、高风险主题和用户要求核实时，必须联网核验；
- 技术问题优先官方文档、规范、源代码和原始研究；
- GitHub 类问题区分默认分支代码、issue 讨论、release 与 commit 历史；
- 工具不可用时输出未执行的 RoutePlan 和明确缺口，不伪装为已检索；
- 用户禁止某来源或联网时，遵守限制并标注由此产生的残余偏倚；
- 不将搜索结果摘要当作原始证据，在可行时打开并核验原页面。

## 9. EvidenceRecord 与 RelationEdge

### 9.1 EvidenceRecord 最小字段

```json
{
  "record_id": "ER-0012",
  "source_id": "doi-or-url-or-repo-sha",
  "version_id": "published-v1",
  "study_family_id": "SF-0007",
  "claim": "...",
  "polarity": "supporting",
  "evidence_kind": "primary-experiment",
  "directness": "direct",
  "method": "...",
  "context": {
    "population_or_system": "...",
    "setting": "...",
    "time": "..."
  },
  "independence_group": "dataset-A",
  "status": "active",
  "provenance": {
    "retrieved_at": "2026-08-16",
    "query_block_id": "QB-004",
    "locator": "..."
  }
}
```

### 9.2 RelationEdge

```json
{
  "source": "A",
  "relation": "compensates_for",
  "target": "B",
  "context": {"system": "..."},
  "assertion_status": "reported",
  "evidence_record_ids": ["ER-0012"],
  "confidence_basis": ["direct perturbation", "independent replication"]
}
```

`assertion_status` 必须区分：

- `reported`：来源明确报告；
- `inferred`：Agent 基于多条证据推断；
- `hypothesized`：仅作为待检索假设；
- `disputed`：存在实质冲突。

不得把共现直接升级为机制关系。

## 10. 去重与独立性

至少执行三层归并：

1. **记录去重**：同 URL、DOI、PMID、仓库 SHA、标准编号；
2. **版本归并**：预印本—会议摘要—正式论文—勘误—撤稿；
3. **证据独立性归并**：同数据集、同队列、同实验系列或二次分析。

输出可以保留全部版本，但决策权重不得把同一研究家族重复计算为多个独立证据。

## 11. BiasLedger

每次复杂任务至少审查：

| 偏倚 | 检测信号 | 补偿动作 |
|---|---|---|
| publication | 几乎只有阳性正式论文 | 搜注册、预印本、会议、失败复现、阴性术语 |
| source | 结果集中于单一平台或机构 | 增加独立来源类 |
| ranking | 只阅读前几条高排名结果 | 分层抽样并执行引文链 |
| terminology | 仅当前术语有结果 | 扩展旧名、缩写、identifier 和跨学科术语 |
| language/region | 仅英语或单一区域 | 视任务增加地区数据库或说明限制 |
| availability | 只使用开放且易获取材料 | 标注不可得原文及摘要证据限制 |
| algorithmic | 推荐结果高度相似 | 使用独立检索式与不同来源类 |
| confirmation | 查询只包含支持性词汇 | 生成反证、失败、无效和边界查询块 |
| authority | 用期刊/组织声望替代内容核验 | 回到原始数据、方法和直接性 |
| AI framing | Agent 过早形成单一叙事 | 先记录替代解释，再综合 |

BiasLedger 字段：`bias_type`、`signal`、`affected_scope`、`compensation`、`residual_risk`、`status`。

## 12. 输出契约

默认输出不应只是一个长参考文献列表。根据任务选择：

### 12.1 快速答案

- 直接结论；
- 一至数个权威来源；
- 时效或关键限制。

### 12.2 检索方案

- RequestProfile 摘要；
- lane 与选择理由；
- QueryBlock 表；
- 来源与工具计划；
- 纳排与去重；
- 偏倚补偿；
- 停止规则；
- 记录与报告格式。

### 12.3 证据地图

- 关键 claims；
- supporting / contradicting / null；
- RelationEdge；
- 情境和方法差异；
- 未解决矛盾；
- 缺口及下一步。

### 12.4 复现包

- 检索日期和查询；
- 来源、版本和标识符；
- 数据、代码、协议和依赖；
- 无法访问或未完成项；
- 运行与验证步骤。

## 13. JSON Schema 与校验脚本

仓库级 schema 负责形状，不负责替代科学判断。随附脚本使用 Python 标准库检查发布所需的高价值结构与跨字段不变量，因此无需额外安装依赖；CI 还应使用支持 JSON Schema 2020-12 的完整 validator 对 schema 做全量验证。

`route-plan.schema.json` 应验证：

- 顶层版本；
- RequestProfile 必填字段；
- lane 只能来自允许枚举；
- 每个 lane 至少一个 QueryBlock；
- QueryBlock 必须有 objective、source classes、status；
- 停止规则和输出契约不可为空。

`evidence-record.schema.json` 应验证：

- provenance 必填；
- polarity、directness、status 使用受控词表；
- inferred edge 不得没有 inference note；
- withdrawn/corrected 状态不得丢失版本信息。

脚本只做确定性检查：

```bash
python scripts/validate_route.py examples/route-plan.json
python scripts/validate_evidence.py examples/evidence-ledger.jsonl
```

不要让脚本自动生成“真实性分数”。

## 14. Skill 内容组织

主 `SKILL.md` 建议保持在约 150–250 行内，只包含：

1. 何时走 fast path；
2. RequestProfile 编译；
3. lane 选择；
4. 查询与来源规划；
5. 证据归一、关系展开和去重；
6. 偏倚审计；
7. 停止规则；
8. 输出契约；
9. 何时读取哪份 reference。

引用路由：

- 选 lane 或解释维度时读 `routing-model.md`；
- 选择来源和工具降级时读 `source-policy.md`；
- 归一证据、建关系或审计偏倚时读 `evidence-and-bias.md`；
- 用户要求可复现计划、证据表或审计记录时读 `output-contracts.md`。

## 15. Eval 方案

### 15.1 数据格式

`evals/cases.jsonl` 每行：

```json
{
  "id": "boundary-simple-fact-01",
  "prompt": "法国首都是哪里？",
  "expected": {
    "trigger": false,
    "max_lanes": 1,
    "must_not": ["full evidence ledger", "bias audit table"]
  }
}
```

复杂用例：

```json
{
  "id": "biomed-bypass-01",
  "prompt": "系统检索靶点 X 被抑制后可能出现的旁通和代偿通路，尤其保留小样本和阴性结果。",
  "expected": {
    "trigger": true,
    "must_lanes": ["direct", "alias", "topology", "contradiction", "long-tail"],
    "must_output": ["relation types", "study-family dedup", "bias ledger", "stop rules"]
  }
}
```

### 15.2 评测层级

1. **Activation**：该触发时触发，不该触发时保持轻量；
2. **Planning**：lane 与 QueryBlock 是否覆盖关键需求；
3. **Trace**：是否使用合适工具并打开原始来源；
4. **Artifact**：输出是否满足 schema 和 output contract；
5. **Truthfulness**：工具失败、原文缺失和推断是否被如实标注；
6. **Efficiency**：简单任务无过度调用，复杂任务能并行独立通道；
7. **Regression**：修改 description 或规则后旧案例不退化。

先建立 10–20 条高信息量用例，再逐步扩展。每次 bug 都新增回归用例。

## 16. GitHub 工作流

仓库创建后：

```bash
git init
git add .
git commit -m "chore: scaffold information router plugin"
git branch -M main
git remote add origin git@github.com:lkh-cq/information-router.git
git push -u origin main
```

建议分支与 PR：

- `feat/router-mvp`：Skill 与 references；
- `feat/router-schemas`：schema 与 validators；
- `test/router-evals`：评测集与评分器；
- `docs/publish-guide`：安装、边界与发布说明；
- `feat/router-mcp`：仅在 M5 决策通过后创建。

GitHub Actions 最小门禁：

1. JSON/YAML 语法；
2. manifest 与目录一致；
3. Skill frontmatter 的 name/description；
4. schema 自身有效；
5. examples 通过 schema；
6. eval 文件可解析；
7. 禁止三元术语和路径依赖的独立性检查；
8. 许可证与版本检查。

独立性检查可扫描：`sanyuan`、`consciousness-bus`、`三元`、`三才`、`ρ`、`θ`、`StoreNode`、`ReadNode` 等标识；文档中若为了声明“不依赖”而出现，可用 allowlist 限定到 ADR 或计划文档。

## 17. 发布门槛

`v0.1.0` 发布前必须满足：

- 插件能被本地 marketplace 识别；
- 直接、间接、追问、负例和边界提示均测试；
- 至少 20 个 eval，用例覆盖 5 个以上领域或信息形态；
- 高风险/当前信息能够强制核验；
- 小论文、阴性结果、旁通路和版本链至少各有一个通过案例；
- 无来源伪造、无工具成功幻觉；
- 核心目录无三元代码或运行时依赖；
- README 明确范围、隐私、限制、许可证和卸载方式；
- 是否引入 MCP 有独立 ADR，而非默认升级。

## 18. 实施顺序

推荐下一步按以下顺序执行：

1. 确认新仓库名、可见性和许可证；
2. 用本轮 scaffold 初始化仓库；
3. 完成 `route-information/SKILL.md` 和四份 reference；
4. 写 10 个边界 eval，再写 10 个复杂 eval；
5. 用最初的医学检索案例端到端验证；
6. 增加软件/GitHub、政策/法规、市场/产品、通用研究四类案例；
7. 加 schema 和纯确定性校验；
8. 本地安装并记录 trace；
9. 评审是否真的需要 MCP；
10. 发布 `v0.1.0`。

## 19. 官方工程依据

- [Build plugins](https://learn.chatgpt.com/docs/build-plugins)：插件可由 Skill、MCP 或两者组成，建议从最小形态开始。
- [Build skills](https://learn.chatgpt.com/docs/build-skills)：Skill 使用渐进披露；`SKILL.md` 保留核心流程，详细材料放 references。
- [Plugin architecture](https://developers.openai.com/plugins/concepts/plugins)：Skill 适合行为与知识，MCP 适合实时数据、鉴权和受控工具。
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)：插件需要 `.codex-plugin/plugin.json`，Skill 放在插件目录中。
- [Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)：测试 direct、indirect、follow-up、negative 与 boundary 提示。
- [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)：以 prompt → trace/artifact → checks → score 的闭环系统评测 Skill。
