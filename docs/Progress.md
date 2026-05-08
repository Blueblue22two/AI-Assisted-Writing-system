# Progress

## 1. 项目理解摘要

本项目是一个用于 Multi-Agent System coursework 的轻量级多智能体学术写作实验系统。项目目标不是构建生产级写作产品，而是实现一个可实验评估的 agent-based system，用于研究结构化 multi-agent plan-execute 写作系统是否比 single-agent baseline 生成质量更高、更稳定的学术文本。

项目范围、技术栈、实验条件、评价指标和实现约束均以 `Product.md` 为最高优先级。

### 核心范围

- 读取 JSONL 写作任务数据集。
- 读取 `configs/config.yaml` 和 `.env` 中的模型 / API 配置。
- 使用 CrewAI 实现 Single-Agent Baseline、Plan-Execute、Plan-Execute-Critique 三个 MVP workflow。
- 使用独立 Evaluator Agent 进行匿名 rubric-based evaluation。
- 保存 agent trace、final answer、evaluation result、runtime 和可用 token usage。
- 聚合结果到 CSV。
- 生成平均分对比图和分数分布图。

### 不属于当前 MVP 的范围

- 复杂 Web 前端。
- 生产级用户系统。
- 实时多人交互。
- 人类受试者实验。
- 复杂 agent negotiation 或完全分布式 agent 通信。
- 大规模训练或微调模型。
- Multi-Critic condition；该项仅作为 A-C 稳定运行后的 optional 扩展。

### 不可变更技术与指标

- 架构：Centralized Orchestrator + Shared Workspace。
- Orchestrator：确定性的 Python workflow controller，不是 LLM-based Agent。
- Agent 编排：CrewAI `Agent`、`Task`、`Crew` 和 sequential workflow。
- 生成类 agents：Planner、Writer、Critic、Editor 默认使用同一生成模型，例如 `deepseek-v4-flash`。
- Evaluator：独立评分器，可使用更强或更稳定的模型，例如 `gpt-5.2`，temperature 固定为 `0.0`。
- 配置：`.env` 管理 API key，`configs/config.yaml` 管理非私密参数。
- 数据与结果：JSONL / CSV。
- 分析与图表：Pandas、Matplotlib / Seaborn。
- 测试：pytest。
- Primary metrics：`overall_score`、`relevance`、`structure`、`evidence_use`、`argument_clarity`、`academic_style`、`grammar_readability`。

`overall_score` 必须按以下方式计算：

```text
overall_score = mean(
  relevance,
  structure,
  evidence_use,
  argument_clarity,
  academic_style,
  grammar_readability
)
```

## 2. 当前状态

### 已完成

- [x] 核心说明文档已存在：`README.md`、`docs/Product.md`、`docs/intro.md`、`docs/Progress.md`、`docs/how to generate data.md`。
- [x] 推荐项目结构中的主要目录与模块文件已创建：`src/`、`src/agents/`、`src/experiments/`、`configs/`、`data/`、`results/`。
- [x] `requirements.txt` 已列出 CrewAI、python-dotenv、Pydantic、PyYAML、Pandas、Matplotlib、Seaborn、pytest 等依赖。
- [x] `configs/config.yaml` 已包含 `llm`、`evaluator_llm` 和 `experiment` 配置。
- [x] `data/tasks_debug.jsonl` 已存在。
- [x] `data/tasks_main.jsonl` 已存在，并已包含 3 条 JSONL writing tasks。
- [x] `data/tasks_main.jsonl` 的 rubric 已统一为六维指标：`relevance`、`structure`、`evidence_use`、`argument_clarity`、`academic_style`、`grammar_readability`。
- [x] 已完成 Phase 1 的核心实现：`src/config.py` 包含 YAML 配置加载、dotenv 环境变量读取、Pydantic 数据模型、JSONL task loader、字段与 rubric 校验及错误路径。
- [x] 已新增 Phase 1 测试：`tests/test_config_and_tasks.py`，覆盖配置读取、环境变量读取、JSONL 解析、字段缺失与 rubric 校验等路径。
- [x] `data/tasks_debug.jsonl` 已修正为六维 rubric（移除 `clarity`，使用 `argument_clarity` 与 `grammar_readability`）。

### 进行中 / 未完成

- [ ] Python 模块多数仍是占位或未完整实现，workflow 端到端仍未可运行（Phase 2-5 待实现）。
- [ ] Shared Workspace、CrewAI workflow、Evaluator、Runner、Analyzer 及对应测试仍需实现。
- [ ] `data/tasks_main.jsonl` 尚未达到正式实验建议规模；当前为 3 条，目标为 25-50 条，MVP 最低不少于 20 条。
- [ ] `.env` 是否存在有效 API key、当前 API endpoint 是否兼容 CrewAI、模型是否可调用仍待通过真实调用确认。

## 3. Phase Progress

> 勾选规则：只有当该 Phase 的全部验收标准都满足，并且不会违反 `Product.md` 约束时，才应将 Phase 标记为完成。

### \[x] Phase 0: 项目骨架与文档基线

**目标**：建立项目说明、推荐目录、配置样例、依赖清单和基础数据文件。

**当前状态**：已完成项目骨架和文档基线；这不代表功能实现完成。

**任务清单**

- [x] 创建核心项目说明文档。
- [x] 创建 `src/`、`src/agents/`、`src/experiments/`、`configs/`、`data/`、`results/` 等目录。
- [x] 创建推荐模块文件：`config.py`、`llm_client.py`、`environment.py`、`orchestrator.py`、`crew_factory.py`、agent modules、runner、analyze。
- [x] 创建 `requirements.txt`。
- [x] 创建 `configs/config.yaml`。
- [x] 创建 debug 和 main JSONL 样例数据文件。
- [x] 创建数据构造教程文档。

**验收标准**

- [x] 文件树中存在推荐结构中的主要文件和目录。
- [x] `requirements.txt` 包含文档要求的主要依赖。
- [x] `configs/config.yaml` 包含 generation LLM、evaluator LLM 和 experiment 配置。
- [x] JSONL 样例文件存在且可被逐行 JSON 解析。

**依赖关系**：无。

### \[x] Phase 1: 配置读取、数据模型与任务加载

**目标**：建立可验证的配置读取、任务读取和核心数据结构，为后续 workflow 提供稳定输入。

**前置条件**

- [x] `configs/config.yaml` 存在。
- [x] `data/tasks_debug.jsonl` 和 `data/tasks_main.jsonl` 存在。
- [x] `.env` 的 API key 状态待确认。(已配置正确，可以写一段代码检查能否正确链接)

**任务清单**

- [x] 实现 `src/config.py`，读取 `configs/config.yaml`。
- [x] 使用 dotenv 读取 `.env` 中的 `LLM_API_KEY` 和 `EVALUATOR_API_KEY`。
- [x] 确保 API key 不写入代码、不写入日志、不提交仓库。
- [x] 定义 LLM 配置、Evaluator 配置和 Experiment 配置的数据模型。
- [x] 定义 writing task 数据模型。
- [x] 实现 JSONL task loader。
- [x] 校验 `task_id`、`instruction`、`source_material`、`target_word_count`、`rubric` 字段完整性。
- [x] 校验 rubric 必须包含六个 primary metrics 字段。
- [x] 对配置缺失、API key 缺失、JSONL 解析失败和任务字段缺失给出明确错误。
- [x] 编写 pytest 覆盖配置读取、任务读取和缺失字段校验。

**验收标准**

- [x] 能从 `configs/config.yaml` 加载非私密配置。
- [x] 能从环境变量读取配置指定的 API key。
- [x] 能读取 `data/tasks_debug.jsonl` 和 `data/tasks_main.jsonl`。
- [x] 任务 schema 与 `Product.md` 的 primary metrics 一致。
- [x] 错误路径明确且不泄露 API key。
- [x] pytest 通过。

**依赖关系**

- 依赖 Phase 0。
- 阻塞 Phase 2、Phase 3、Phase 4、Phase 5。

### \[ ] Phase 2: Shared Workspace、LLM Client 与 Agent Prompt

**目标**：实现 language-based academic writing environment 的状态模型和 LLM 调用基础设施，并定义各 agent 的职责、输入和输出。

**前置条件**

- [x] Phase 1 完成。
- [x] API endpoint、模型名称和 key 可用性已确认，或代码中具备清晰错误路径。

**任务清单**

- [ ] 在 `src/environment.py` 定义 writing environment 和 shared workspace。
- [ ] Shared Workspace 保存 task、source material、rubric、condition、repetition、plan、draft、critique、final answer、evaluation result、runtime、model information、token usage。
- [ ] 在 `src/llm_client.py` 封装 OpenAI-compatible API 调用，供 Evaluator 或非 CrewAI 调用使用。
- [ ] 在 `src/agents/planner.py` 定义 Planner Agent 的 role、goal、prompt 和 expected output。
- [ ] 在 `src/agents/writer.py` 定义 Writer Agent 的 role、goal、prompt 和 expected output。
- [ ] 在 `src/agents/critic.py` 定义 Critic Agent 的 role、goal、prompt 和 expected output。
- [ ] 在 `src/agents/editor.py` 定义 Editor Agent 的 role、goal、prompt 和 expected output。
- [ ] 在 `src/agents/evaluator.py` 定义 Evaluator Agent 的固定评分 prompt 和 JSON 输出要求。
- [ ] 确保 Evaluator prompt 不包含 condition、workflow、plan、draft、critique 或 run metadata。
- [ ] 编写 pytest 覆盖 workspace 状态更新和 evaluator schema 校验。

**验收标准**

- [ ] Shared Workspace 能表达 Product.md 中列出的初始状态、中间状态和终止状态。
- [ ] Planner 输出 thesis statement、paragraph outline、key arguments、evidence plan。
- [ ] Writer 输出 academic draft 或 final answer。
- [ ] Critic 输出 structured critique、weaknesses、revision suggestions。
- [ ] Editor 输出 revised final answer。
- [ ] Evaluator 输出可解析 JSON：`eval_id`、`scores`、`overall_score`、`justification`。
- [ ] LLM client 不记录 API key。
- [ ] pytest 通过。

**依赖关系**

- 依赖 Phase 1。
- 阻塞 Phase 3 和 Phase 4。

### \[ ] Phase 3: CrewAI Workflow 与确定性 Orchestrator

**目标**：用 CrewAI 实现三个 MVP 实验条件，并由确定性 Python Orchestrator 控制运行顺序。

**前置条件**

- [ ] Phase 1 完成。
- [ ] Phase 2 完成。
- [ ] CrewAI 依赖可安装并可导入。

**任务清单**

- [ ] 在 `src/crew_factory.py` 创建 CrewAI agents。
- [ ] 在 `src/crew_factory.py` 创建 CrewAI tasks。
- [ ] 在 `src/crew_factory.py` 创建 Condition A crew：Single-Agent Baseline。
- [ ] 在 `src/crew_factory.py` 创建 Condition B crew：Plan-Execute。
- [ ] 在 `src/crew_factory.py` 创建 Condition C crew：Plan-Execute-Critique。
- [ ] 使用 CrewAI sequential process，不引入 agent 自由对话或 negotiation。
- [ ] 在 `src/orchestrator.py` 根据 condition 调用不同 crew。
- [ ] 保持 Orchestrator 为确定性 Python workflow controller，不实现为 Manager Agent 或 LLM-based Coordinator。
- [ ] 每次 workflow 运行后更新 Shared Workspace。
- [ ] 记录 plan、draft、critique、final answer、runtime、model config 和可用 token usage。
- [ ] 将 generation trace 序列化为 JSONL 兼容结构。

**验收标准**

- [ ] Condition A 可由同一任务输入运行，并只输出 final answer。
- [ ] Condition B 可运行，并输出 plan 和 final answer。
- [ ] Condition C 可运行，并输出 plan、draft、critique 和 final answer。
- [ ] Orchestrator 不调用 LLM 决策下一步流程。
- [ ] Agent outputs 可保存到 shared workspace。
- [ ] 运行记录可序列化为 `results/runs.jsonl`。

**依赖关系**

- 依赖 Phase 2。
- 阻塞 Phase 4 和 Phase 5。

### \[ ] Phase 4: 独立匿名评估流程

**目标**：实现正式评估所需的匿名化、独立 evaluator 调用、JSON 解析和评分记录。

**前置条件**

- [ ] Phase 3 能生成 final answer。
- [ ] Evaluator 配置可用。

**任务清单**

- [ ] 从 generation outputs 生成匿名 `evaluation_items.jsonl`。
- [ ] 每条 evaluation item 只包含 `eval_id`、`task_id`、`instruction`、`source_material`、`target_word_count`、`rubric` 和 `answer`。
- [ ] 单独保存 `eval_id` 与 `condition`、`repetition_id` 的内部映射，不传给 Evaluator。
- [ ] 打乱 evaluation item 顺序。
- [ ] 调用独立 Evaluator Agent 或统一 `llm_client` 评分。
- [ ] 解析 evaluator JSON。
- [ ] 校验所有 score 是 1-5 的整数。
- [ ] 根据六个维度重新计算 `overall_score`，用于一致性检查。
- [ ] 如果 JSON 解析失败，执行一次 repair prompt。
- [ ] 如果 repair 后仍失败，将该 evaluation 标记为 `parse_failed`，不得手动猜测分数。
- [ ] 写入 `results/evaluation_results.jsonl`。
- [ ] 写入 `results/scores.csv`。
- [ ] 编写 pytest 覆盖匿名化字段、JSON 解析、repair fallback 和 overall score 计算。

**验收标准**

- [ ] Evaluator 输入不包含 condition、workflow、plan、draft、critique 或 run metadata。
- [ ] `evaluation_items.jsonl` 可追踪但对 Evaluator 匿名。
- [ ] `evaluation_results.jsonl` 保存 evaluator 原始评分输出。
- [ ] `scores.csv` 可被 pandas 读取。
- [ ] JSON 解析失败路径可测试。
- [ ] pytest 通过。

**依赖关系**

- 依赖 Phase 3。
- 阻塞 Phase 5。

### \[ ] Phase 5: Runner、结果聚合与图表

**目标**：实现批量实验运行、结果聚合和 coursework report 所需图表输出。

**前置条件**

- [ ] Phase 4 完成。
- [ ] `data/tasks_main.jsonl` 已达到正式实验所需规模，或明确标记当前仅能运行 debug / smoke test。

**任务清单**

- [ ] 在 `src/experiments/runner.py` 实现 CLI 参数解析。
- [ ] runner 支持读取 `--config` 和 `--tasks`。
- [ ] runner 支持按 `experiment.repetitions` 运行。
- [ ] runner 支持 A、B、C 三个 MVP conditions。
- [ ] runner 写入 `results/runs.jsonl`。
- [ ] runner 写入 `results/evaluation_items.jsonl`。
- [ ] runner 写入 `results/evaluation_results.jsonl`。
- [ ] runner 写入 `results/scores.csv`。
- [ ] 在 `src/experiments/analyze.py` 实现结果读取。
- [ ] analyze 聚合 `task_id + condition` 的 repetitions。
- [ ] analyze 输出 `results/summary.csv`。
- [ ] analyze 计算 mean score、standard deviation、mean difference、win / tie / loss count、win rate。
- [ ] analyze 生成 `results/charts/mean_scores.png`。
- [ ] analyze 生成 `results/charts/score_distribution.png`。
- [ ] 如时间允许，补充 Wilcoxon signed-rank test；该项不得替代 primary metrics。
- [ ] 编写 pytest 或最小 smoke test 覆盖 runner 参数解析和 analyze 聚合逻辑。

**验收标准**

- [ ] 可以运行 `python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl`。
- [ ] 可以运行 `python -m src.experiments.analyze --results results/runs.jsonl` 或项目实现中等价命令。
- [ ] 输出文件路径符合 Product.md 的 Result Files 要求。
- [ ] 若 token usage 不可用，结果中明确标记为 optional / unavailable，不伪造 token 或 cost。
- [ ] 图表文件存在且可打开。
- [ ] pytest 或 smoke test 通过。

**依赖关系**

- 依赖 Phase 4。
- 阻塞 Phase 6。

### \[ ] Phase 6: 数据集扩充、正式实验与结论边界

**目标**：完成 coursework 最低可接受实验规模，并形成可用于报告的结果。

**前置条件**

- [ ] Phase 5 完成。
- [ ] API 调用成本和运行时间可接受。
- [ ] 模型和 endpoint 已通过 debug set smoke test。

**任务清单**

- [ ] 将 `data/tasks_debug.jsonl` 扩充到 3-5 条。
- [ ] 将 `data/tasks_main.jsonl` 扩充到至少 20 条正式 writing tasks。
- [ ] 优先目标：将 `data/tasks_main.jsonl` 扩充到 25-50 条高质量 writing tasks。
- [ ] 确保任务不使用真实学生作文。
- [ ] 确保任务不收集真实用户数据。
- [ ] 确保 source material 短小、可控，并覆盖多个学术方向。
- [ ] 用 debug set 运行 prompt debugging 和流程测试。
- [ ] 运行正式实验：至少 20 tasks x 3 conditions x 3 repetitions。
- [ ] 检查 `runs.jsonl`、`evaluation_items.jsonl`、`evaluation_results.jsonl`、`scores.csv`、`summary.csv` 和 charts 完整性。
- [ ] 在 coursework report 中讨论 LLM-as-judge 限制。
- [ ] 在 coursework report 中讨论小规模任务集限制。
- [ ] 在 coursework report 中讨论 multi-agent 的 token cost 和 runtime 代价。
- [ ] 将结论限定为“在本项目任务集、模型配置和评分协议下”。

**验收标准**

- [ ] 至少 20 个正式 writing tasks。
- [ ] A、B、C 三个 conditions 每个任务至少重复 3 次。
- [ ] 完整保存 generation trace 和 evaluation result。
- [ ] 输出 mean score、standard deviation、win rate。
- [ ] 输出平均分柱状图和分数分布图。
- [ ] 结论不泛化为 multi-agent writing systems 普遍优于 single-agent systems。

**依赖关系**

- 依赖 Phase 5。
- 依赖可用 API key、可用模型和可接受预算。

### \[ ] Phase 7: Optional Multi-Critic 扩展

**目标**：在 MVP 稳定完成后，评估是否加入多个 Critic Agent 从不同角度批评初稿。

**前置条件**

- [ ] Phase 6 完成。
- [ ] A、B、C 三个 conditions 已稳定运行。
- [ ] 结果分析流程完整。
- [ ] 成本和时间允许。

**任务清单**

- [ ] 确认是否需要 Condition D: Multi-Critic。
- [ ] 如确认需要，定义 Structure Critic Agent。
- [ ] 如确认需要，定义 Evidence Critic Agent。
- [ ] 如确认需要，定义 Style Critic Agent。
- [ ] 设计 Editor 汇总多个 critic 反馈的输入格式。
- [ ] 记录 Multi-Critic 带来的 token cost 和 runtime 增量。
- [ ] 将 Multi-Critic 结果作为 optional extension，而不是 MVP 核心证据。

**验收标准**

- [ ] Condition D 不影响 A、B、C 的 MVP 实验结论。
- [ ] Multi-Critic 的成本、收益和限制被单独报告。
- [ ] 不将 optional 结果写成核心必需结果。

**依赖关系**

- 依赖 Phase 6。
- 当前状态：待确认。

## 4. 风险、阻塞与待确认事项

| 风险 / 阻塞                                    | 影响范围                     | 需要确认的问题                                                             | 建议处理方式                                                      |
| ------------------------------------------ | ------------------------ | ------------------------------------------------------------------- | ----------------------------------------------------------- |
| API key 和模型可用性未确认                          | LLM 调用、实验运行、Evaluator 评分 | `.env` 是否存在有效 key；API provider 是否支持 `deepseek-v4-flash` 和 `gpt-5.2` | 实现启动前校验；错误信息不泄露 key                                         |
| CrewAI 与 OpenAI-compatible endpoint 兼容性未确认 | Workflow 执行              | 当前 endpoint 是否能被 CrewAI 正确调用                                        | 先用 debug task 做 smoke test                                  |
| 当前正式数据不足                                   | 正式实验与 coursework 最低要求    | `tasks_main.jsonl` 当前只有 3 条，Product.md MVP 至少需要 20 条正式 tasks        | 在正式实验前扩充到至少 20 条，优先目标 25-50 条                               |
| 当前代码仍未完整实现                                 | 所有功能实现                   | Python 模块尚未形成完整可运行逻辑                                                | 按 Phase 1-5 逐步实现并测试                                         |
| Token usage / cost 可能不可用                   | 成本分析                     | API provider 是否返回 token usage                                       | Product.md 允许 MVP 先记录 runtime，并将 token / cost 标记为 optional  |
| Evaluator JSON 解析失败                        | 评分流程                     | LLM 是否稳定输出纯 JSON                                                    | 固定 prompt；失败后 repair 一次；仍失败标记 `parse_failed`                |
| LLM-as-judge 偏差                            | 实验结论可信度                  | Evaluator Agent 是否存在模型偏好或评分偏差                                       | 匿名化、固定 prompt、固定 temperature，并在 report 中说明限制                |
| 小规模任务集限制                                   | 结论外推                     | 20-50 条任务不能证明所有学术写作场景                                               | 结论限定为“本项目设定的任务集、模型配置和评分协议下”                                 |
| Multi-agent 成本更高                           | 实验预算和 runtime            | A-C 三个 conditions x 3 repetitions 的调用成本是否可接受                        | 先运行 debug set，再运行 main set；记录 runtime 和 optional token/cost |

## 5. 不可变更约束

以下约束来自 `Product.md`，Progress.md 中所有 Phase 和任务拆分必须服从这些约束。

### 产品目标约束

- 项目目标是 coursework 用轻量级实验系统，不是生产级写作产品。
- 研究问题必须围绕 multi-agent plan-execute writing workflow 是否优于 single-agent baseline。
- 实验结论不得泛化为 multi-agent writing systems 普遍优于 single-agent systems。
- 不包含复杂 Web 前端、生产级用户系统、实时多人交互、人类受试者实验、复杂 agent negotiation、完全分布式 agent 通信、大规模训练或微调模型。

### 架构约束

- 必须采用 Centralized Orchestrator + Shared Workspace 架构。
- Orchestrator 必须是确定性的 Python workflow controller。
- Orchestrator 不是 LLM-based Agent，不应默认实现为 Manager Agent 或 Coordinator Agent。
- Agents 不直接自由通信；通过 shared workspace 读取和写入中间结果。
- MVP 只使用一轮 critique-revision。

### 技术栈约束

- 使用 Python。
- 使用 CrewAI 作为轻量级 multi-agent 编排框架。
- 使用 OpenAI-compatible API client 调用外部 LLM。
- 使用 YAML / dotenv 管理配置和 API key。
- 使用 Pydantic 定义结构化输出和 evaluation result。
- 使用 JSONL / CSV 保存任务数据、运行日志和评分结果。
- 使用 Pandas 聚合实验结果。
- 使用 Matplotlib / Seaborn 生成图表。
- 使用 pytest 测试配置读取、数据加载、评分解析和 workflow。
- 不得在未确认前引入 Product.md 未明确允许的新技术、新架构、新工具、新平台或新评估指标。

### 模型与配置约束

- Planner、Writer、Critic、Editor 默认使用同一生成模型，例如 `deepseek-v4-flash`。
- Evaluator 可以使用独立且更强或更稳定的模型，例如 `gpt-5.2`。
- Evaluator temperature 固定为 `0.0`。
- 生成类 agent temperature 可设置为 `0.3-0.6`。
- Critic temperature 可设置为 `0.2-0.3`。
- API key 不写入代码、不写入日志、不提交到仓库。
- config 文件只保存 endpoint、model name、temperature、max\_tokens 等非私密信息。

### 实验条件约束

- MVP 必须实现并比较：
  - Condition A: Single-Agent Baseline。
  - Condition B: Plan-Execute。
  - Condition C: Plan-Execute-Critique。
- Condition D: Multi-Critic 是可选扩展，只有在 A-C 稳定运行、结果分析流程完整后再考虑。
- 所有 conditions 必须使用相同 task、source material、target word count 和 rubric。
- 每个 condition 至少重复 3 次。

### 评估约束

- Evaluator Agent 不参与 generation crew。
- Evaluator 是统一评分器，所有 conditions 使用同一个 evaluator 配置。
- Evaluator 不应知道答案来自哪个 condition。
- Evaluator 不应接收 agent workflow、plan、draft、critique 或 run metadata。
- 正式评估前必须将 final answer 转换为匿名 evaluation item，并打乱评估顺序。
- Evaluator 必须输出可解析 JSON，不应输出 Markdown 或额外解释文字。
- JSON 解析失败时最多进行一次 repair prompt；仍失败则标记为 `parse_failed`，不得手动猜测分数。
- 即使 Evaluator 输出 `overall_score`，系统仍应根据六个维度重新计算一次用于一致性检查。

### 指标约束

- 本项目只设置 primary metrics。
- Primary metrics 必须直接对应 Evaluator Agent 的 rubric scores：
  - `overall_score`
  - `relevance`
  - `structure`
  - `evidence_use`
  - `argument_clarity`
  - `academic_style`
  - `grammar_readability`
- `overall_score` 必须按六个维度平均值计算。
- Cost 和 runtime 需要记录和讨论，但不作为 primary metrics。
- 如果 API provider 不返回 token usage，MVP 可以先记录 runtime，并将 token / cost 标记为 optional；不得伪造 token 或 cost。

### 数据约束

- 推荐 5 个任务用于 prompt debugging。
- 推荐 20-50 个任务用于正式实验；MVP 最低应至少 20 个正式 writing tasks。
- 当前数据构造文档提出目标为 25-50 条高质量数据。
- 不使用真实学生作文。
- 不收集真实用户交互数据。
- source material 应短小、可控，避免上下文过长导致成本上升。
- 任务主题应覆盖多个学术方向，避免只测试一个主题。

