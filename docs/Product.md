# Product Specification：轻量级多智能体学术写作辅助系统

## 1. 项目概述
本项目实现一个轻量级的多智能体学术写作辅助系统，用于完成 Multi-Agent System 方向的 coursework。
- 核心目标：
不是构建一个生产级写作工具，而是设计一个可实验评估的 agent-based system，用来研究结构化多智能体协作是否能够相比单智能体基线提升学术写作质量。
- Task:
系统以语言型写作任务作为环境。给定写作题目、参考材料、目标字数和评分标准，不同智能体分别承担规划、写作、批评、编辑和评分等角色，并通过中心化流程协作完成写作任务。

## 2. Coursework 要求对齐

该 coursework 要求项目包含四个核心部分：
- **Environment**：智能体运行的环境。本项目采用 language-based academic writing environment。
- **Autonomous Agents**：一个或多个使用 AI 方法完成任务的智能体。本项目使用多个 LLM-based agents。
- **Question**：围绕系统提出具体研究问题。本项目关注多智能体协作是否提升写作质量。
- **Experiments**：通过多次运行和统计分析回答研究问题。本项目会比较不同 agent 架构下的写作质量、稳定性、成本和运行时间。

## 3. 研究问题

**主研究问题**：  
在相同写作任务和评分标准下，轻量级 multi-agent plan-execute 写作系统是否比 single-agent baseline 生成质量更高、更稳定的学术文本？

进一步研究问题（Optional）：
- 加入 Planner Agent 是否能改善文本结构？
- 多智能体协作是否会带来更高 token cost 和 runtime？
- 如果加入多个 Critic Agent，从不同角度批评文本，是否比单个 Critic Agent 更有效？

## 4. 项目范围

项目包含：
- Python 实现的轻量级多智能体写作系统。
- 使用 CrewAI 作为轻量级 multi-agent 编排框架，避免全程手写 agent/task/workflow 逻辑。
- 中心化 orchestrator 管理 agent 调用顺序。
- 外部 LLM API 调用。
- 使用配置文件统一管理模型、API endpoint、temperature 等参数。
- 使用环境变量管理 API key。
- 自动保存 agent 中间输出和实验结果。
- 自动 rubric-based evaluation。
- 使用统计分析和图表比较实验条件。

项目不包含：
- 复杂 Web 前端。
- 生产级用户系统。
- 实时多人交互。
- 人类受试者实验。
- 复杂 agent negotiation 或完全分布式 agent 通信。
- 大规模训练或微调模型。

## 5. Multi-Agent System 架构

本项目采用 **Centralized Orchestrator + Shared Workspace** 架构。
系统中存在一个中心控制器：
- Orchestrator 负责决定每个 agent 何时执行。
- Agents 不直接自由通信。
- Agents 通过 shared workspace 读取和写入中间结果。
- 所有状态变化和 agent 输出都会被记录，方便实验分析。

在最小可行版本中，**Orchestrator 应该是一段确定性的 Python workflow controller，而不是一个 LLM-based Agent**。它不负责生成内容，也不需要调用 LLM；它只负责执行固定流程、传递状态、记录日志和切换实验条件。具体实现上，可以由 Python Experiment Runner 调用 CrewAI 的 `Crew`、`Agent`、`Task` 和 sequential process 来完成多智能体执行。这样既避免全程手写 agent 编排代码，也能保持实验流程可控、轻量和容易解释。

不建议默认把 Orchestrator 设计成 Manager Agent 或 Coordinator Agent。虽然这种方式可以让 LLM 动态决定下一步调用哪个 agent，但会增加 prompt 设计、成本、随机性和结果解释难度。对于本 coursework，更清晰的定义是：

- Orchestrator = deterministic code controller
- Planner / Writer / Critic / Editor / Evaluator = LLM-based Agents

选择中心化架构的原因：

- 实现轻量，适合 coursework 时间规模。
- 便于控制实验变量。
- 便于记录完整 agent trace。
- 便于比较 single-agent 和 multi-agent 条件。
- 避免复杂的异步通信、冲突解决和 agent negotiation。

系统核心组件：

- **Orchestrator**：中心编排器，负责 workflow 控制、CrewAI crew 调用、日志记录和实验条件切换。
- **Shared Workspace**：共享工作区，保存任务、参考材料、写作计划、初稿、批评意见、修订稿、评分和运行信息。
- **Agent Modules**：不同职责的 CrewAI agents，包括 planner、writer、critic、editor 和 evaluator。
- **Experiment Runner**：批量运行多个任务和多个实验条件。
- **Result Analyzer**：聚合结果，计算统计指标并生成图表。

## 6. Agent 设计

推荐使用以下 agents：

### Planner Agent

职责：

- 理解写作任务。
- 提出中心论点。
- 设计文章结构。
- 决定每个段落的功能。
- 从参考材料中规划可用证据。

输入：

- writing instruction
- source material
- rubric
- target word count

输出：

- thesis statement
- paragraph outline
- key arguments
- evidence plan

### Writer Agent

职责：

- 根据 Planner Agent 的计划生成初稿。
- 保持学术语气。
- 遵守目标字数和 rubric 要求。

输入：

- writing instruction
- source material
- writing plan
- rubric

输出：

- academic draft

### Critic Agent

职责：

- 根据 rubric 检查初稿质量。
- 找出结构、论证、证据使用、清晰度和学术风格方面的问题。
- 给出可执行的修改建议。

输入：

- writing instruction
- source material
- rubric
- draft

输出：

- structured critique
- weaknesses
- revision suggestions

### Editor Agent

职责：

- 根据 Critic Agent 的反馈修改初稿。
- 保留原始任务要求。
- 改善结构、论证和语言表达。

输入：

- writing instruction
- source material
- draft
- critique
- rubric

输出：

- revised final answer

### Evaluator Agent

职责：

- 根据固定 rubric 对最终文本评分。
- 输出结构化 JSON 分数。
- 提供简短评分理由。

输入：

- writing instruction
- source material
- rubric
- final answer

输出：

- dimension scores
- overall score
- justification

可选扩展（Optional，当前不需要）：
- **Structure Critic Agent**：专门检查结构和逻辑。
- **Evidence Critic Agent**：专门检查证据使用。
- **Style Critic Agent**：专门检查学术语气和表达质量。

## 7. Plan-Execute 与 ReAct 的选择

本项目核心流程采用 **Plan-Execute 范式**。

推荐 workflow：

```text
Task + Source + Rubric
        |
        v
Planner Agent
        |
        v
Writer Agent
        |
        v
Critic Agent
        |
        v
Editor Agent
        |
        v
Evaluator Agent
```

选择 Plan-Execute 的原因：
- 学术写作天然适合“规划 -> 写作 -> 批评 -> 修改 -> 评分”的流程。
- 系统行为更容易控制和复现实验。
- 实现更轻量。
- 中间输出更清晰，便于 coursework report 分析。
- 与项目目标更匹配。

## 8. 不同 Agent 是否需要使用不同 LLM 模型
默认设置：
- Planner、Writer、Critic、Editor 全部使用同一个生成模型，例如 `deepseek-v4-flash`。
- Evaluator 使用更强或更稳定的独立模型，例如 `gpt-5.2`。
- Evaluator 使用固定 rubric 和固定评分 prompt。
- Evaluator 不接收文本来自哪个 condition 的信息。
- Evaluator temperature 设置为 `0.0`，保证评分更稳定。
- 生成类 agent temperature 可设置为 `0.3-0.6`。
- Critic temperature 可设置得较低，例如 `0.2-0.3`。

**Evaluator Agent 可以使用不同的 LLM 模型**，而且这是一个合理的实验设计选择。Evaluator 的角色是统一评分器，而不是被比较的生成系统的一部分。使用不同模型作为 Evaluator 有助于降低生成模型对自身输出的偏好，并提高评分稳定性。

在实验报告中应明确说明：被比较的是不同 writing workflow 或 agent architecture，例如 Single-Agent、Plan-Execute、Plan-Execute-Critique；Evaluator 是统一的 evaluation instrument，所有 condition 都由同一个 Evaluator 配置评分。因此，即使 Evaluator 使用不同 LLM，实验比较仍然是公平的。

可选扩展实验（Optional）：
- 使用强模型作为 Evaluator，便宜模型作为其他 agents。
- 比较 same-model multi-agent 与 mixed-model multi-agent。
- 比较 strong single-agent 与 cheap multi-agent。

## 9. LLM 调用与配置管理

所有 LLM 调用都使用外部 API key，并通过配置文件统一管理。
建议使用 `.env` 和 `configs/config.yaml` 管理配置：

### `.env`

用于存放私密信息，不提交到 Git。

示例：

```env
LLM_API_KEY=your_api_key_here
EVALUATOR_API_KEY=your_evaluator_api_key_here
```

### `configs/config.yaml`

用于存放非私密配置。

示例：

```yaml
llm:
  provider: "openai-compatible"
  base_url: "https://api.example.com/v1"
  api_key_env: "LLM_API_KEY"
  default_model: "deepseek-v4-flash"
  temperature: 0.4
  max_tokens: 1200

evaluator_llm:
  provider: "openai-compatible"
  base_url: "https://api.example.com/v1"
  api_key_env: "EVALUATOR_API_KEY"
  model: "gpt-5.2"
  temperature: 0.0
  max_tokens: 1000

experiment:
  repetitions: 3
  output_dir: "results"
```

重要原则：

- API key 不写入代码。
- API key 不写入实验日志。
- config 文件只存储 endpoint、model name、temperature、max tokens 等非私密信息。
- CrewAI generation agents 使用 `llm` 配置。
- Evaluator 使用 `evaluator_llm` 配置，并作为独立评分器。
- 非 CrewAI 调用或 Evaluator 调用可以统一经过 `llm_client` 模块。

## 10. Environment 设计

本项目的 environment 是一个 **language-based academic writing environment**。
每个 episode 对应一个写作任务。

### 初始环境状态

包括：

- task_id
- writing instruction
- source material
- target word count
- rubric

### 中间环境状态

包括：

- plan
- draft
- critique
- revised answer
- final answer
- evaluation result
- token usage
- runtime
- model information
- workflow condition

### Agent 可执行动作

包括：

- `plan`
- `write`
- `critique`
- `revise`
- `evaluate`

### 状态转移

每个 agent 执行后，environment 会更新 shared workspace。例如：

- Planner Agent 执行后写入 `plan`。
- Writer Agent 执行后写入 `draft`。
- Critic Agent 执行后写入 `critique`。
- Editor Agent 执行后写入 `final_answer`。
- Evaluator Agent 执行后写入 `evaluation_result`。

### Episode 终止条件

- final answer 已生成并完成 evaluation。
- 或达到最大 revision round 数量。

最小可行版本建议只使用一轮 critique-revision。

## 11. Experiments 设计

实验目标是比较不同 agent 架构下的写作质量和运行成本。

推荐实验条件：

### Condition A：Single-Agent Baseline

一个 LLM 直接接收 task、source material、rubric 和 target word count，并生成最终文本。

目的：

- 作为最基础 baseline。
- 检验多智能体协作是否真正带来提升。

### Condition B：Plan-Execute

Planner Agent 先生成写作计划，Writer Agent 根据计划写作。

目的：

- 检验“显式规划”是否提升文本结构和论证质量。

### Condition C：Plan-Execute-Critique

Planner Agent -> Writer Agent -> Critic Agent -> Editor Agent。

目的：

- 检验 critic-editor revision 是否提升最终文本质量。
- Workflow 结束后，由独立 Evaluator Agent 统一评分。

### Condition D：Multi-Critic，可选

多个 critic 从不同角度评价初稿，例如：

- structure critic
- evidence critic
- style critic

Editor Agent 汇总所有反馈后生成最终文本。

目的：

- 检验多角度批评是否优于单一 critic。

推荐实验设置：

- 20-50 个写作任务。
- 每个任务在所有 condition 下运行。
- 每个 condition 重复运行 3 次。
- 所有 condition 使用相同 task、source material 和 rubric。
- 记录每次运行的 agent trace、最终文本、分数、成本和时间。

---

## 12. Evaluation and Experiment Protocol

本项目的评估目标不是证明系统在所有写作场景中绝对优于单智能体，而是在 coursework 可控范围内，检验不同 agent workflow 在相同任务、相同材料和相同评分标准下是否带来可观察的质量差异、稳定性差异和成本差异。

因此，本项目采用小规模、可复现、paired experimental design。每个写作任务都会在所有实验条件下运行，并由同一个独立 Evaluator Agent 使用固定 rubric 进行匿名评分。

### 12.1 Evaluation Goals

评估主要回答以下问题：

1. **质量提升**：Multi-agent workflow 是否比 single-agent baseline 生成更高质量的学术文本？
2. **结构收益**：加入 Planner Agent 是否改善文章结构、论证组织和任务覆盖度？
3. **修订收益**：加入 Critic + Editor 是否改善最终答案质量？
4. **稳定性**：Multi-agent workflow 是否降低不同运行之间的分数波动？
5. **成本代价**：质量提升是否伴随更高 token usage、runtime 和 estimated cost？

### 12.2 Experimental Conditions

最小可行版本比较三个核心条件。

#### Condition A: Single-Agent Baseline

一个 Writer Agent 直接接收：

- writing instruction
- source material
- target word count
- rubric

并直接输出 final answer。

该条件作为基础 baseline，用于判断 multi-agent workflow 是否真正带来收益。

#### Condition B: Plan-Execute

Workflow:

```text
Planner Agent -> Writer Agent
```

Planner Agent 先生成 writing plan，Writer Agent 根据 plan 和 source material 生成 final answer。

该条件用于检验显式规划是否改善文本结构、论点清晰度和证据安排。

#### Condition C: Plan-Execute-Critique

Workflow:

```text
Planner Agent -> Writer Agent -> Critic Agent -> Editor Agent
```

Writer Agent 先生成 draft，Critic Agent 根据 rubric 提供 critique，Editor Agent 根据 critique 修订并输出 final answer。

该条件用于检验 critique-revision loop 是否提升最终文本质量。

#### Optional Condition D: Multi-Critic

Multi-Critic 暂不作为 MVP 必需条件。只有在 Condition A-C 已经稳定运行、结果分析流程完整后，再考虑加入。

建议原因：

- Multi-Critic 会显著增加 token cost 和 runtime。
- 多个 critic 的反馈合并会引入额外 prompt 设计复杂度。
- 对 coursework 来说，A-C 已足够回答核心研究问题。

### 12.3 Dataset and Repetitions

实验数据分为两部分：

- `tasks_debug.jsonl`：用于 prompt debugging 和流程测试，建议 3-5 条。
- `tasks_main.jsonl`：用于正式实验，建议 20 条左右。

虽然原始设计中建议 20-50 条正式任务，但考虑 coursework 时间、API 成本和实验可控性，MVP 推荐使用：

```text
20 tasks x 3 conditions x 3 repetitions = 180 generation runs
```

每条任务应包含：

```json
{
  "task_id": "T001",
  "instruction": "Write a 250-word critical paragraph about ...",
  "source_material": "Short source material or background notes.",
  "target_word_count": 250,
  "rubric": {
    "relevance": 5,
    "structure": 5,
    "evidence_use": 5,
    "academic_style": 5,
    "clarity": 5
  }
}
```

任务设计原则：

- 不使用真实学生作文。
- 不收集真实用户数据。
- source material 应短小、可控，避免上下文过长导致成本上升。
- 任务主题应覆盖多个学术方向，避免只测试一个主题。
- 所有 conditions 必须使用完全相同的 task、source material、target word count 和 rubric。

### 12.4 Evaluation Method

本项目使用独立 Evaluator Agent 进行 rubric-based evaluation。

Evaluator Agent 不参与文本生成 workflow。它只负责对 final answer 评分。所有 conditions 的输出都由同一个 evaluator 配置评分，以保证比较的一致性。

Evaluator 输入包括：

- writing instruction
- source material
- target word count
- rubric
- anonymized final answer

Evaluator 不应接收：

- condition name
- agent workflow
- plan
- draft
- critique
- run metadata

这样可以减少 evaluator 对某种 workflow 的偏见。

### 12.5 Anonymization and Randomization

为了降低评分偏差，正式评估前应将所有 final answers 转换为匿名 evaluation items。

每条 evaluation item 只包含：

```json
{
  "eval_id": "E0001",
  "task_id": "T001",
  "instruction": "...",
  "source_material": "...",
  "target_word_count": 250,
  "rubric": {...},
  "answer": "..."
}
```

`eval_id` 与真实 `condition`、`repetition_id` 的映射应单独保存在内部结果记录中，不传给 Evaluator Agent。

评估顺序应打乱，避免 evaluator 因顺序模式推断 condition。

### 12.6 Rubric Dimensions

Evaluator 使用 1-5 分制评价以下维度。每个维度的评分描述使用英文，以便直接放入 evaluator prompt 中。

#### Relevance

Evaluates whether the answer directly addresses the writing task and remains focused on the instruction.

- 1: The answer is largely irrelevant or fails to address the task.
- 2: The answer only partially addresses the task and misses major requirements.
- 3: The answer addresses the task in a basic way but may be incomplete or generic.
- 4: The answer is relevant and covers most task requirements clearly.
- 5: The answer fully addresses the task with strong focus and no major omissions.

#### Structure and Coherence

Evaluates the organization of ideas, paragraph structure, logical flow, and coherence.

- 1: The answer is disorganized and difficult to follow.
- 2: The answer has weak organization with unclear connections between ideas.
- 3: The answer has a basic structure, but the flow or transitions are limited.
- 4: The answer is well organized with mostly clear logical progression.
- 5: The answer is highly coherent, well structured, and logically developed.

#### Evidence Use

Evaluates how effectively the answer uses the source material or background information to support claims.

- 1: The answer does not use the source material or uses it inaccurately.
- 2: The answer makes minimal or vague use of the source material.
- 3: The answer uses some relevant evidence, but support is limited or underdeveloped.
- 4: The answer uses relevant evidence appropriately to support most claims.
- 5: The answer uses source material accurately, specifically, and effectively throughout.

#### Argument Clarity

Evaluates whether the central argument is clear, well reasoned, and critically developed.

- 1: The answer lacks a clear argument or contains flawed reasoning.
- 2: The argument is weak, unclear, or insufficiently developed.
- 3: The answer presents a basic argument, but reasoning may be shallow or uneven.
- 4: The argument is clear, reasonable, and mostly well developed.
- 5: The argument is precise, persuasive, and shows strong critical reasoning.

#### Academic Style

Evaluates whether the language is appropriate for academic writing.

- 1: The language is informal, inappropriate, or unsuitable for academic writing.
- 2: The language is sometimes informal, vague, or imprecise.
- 3: The style is generally academic but may contain repetitive or generic phrasing.
- 4: The language is clear, formal, and mostly precise.
- 5: The language is consistently formal, precise, objective, and academically appropriate.

#### Grammar and Readability

Evaluates grammatical accuracy, fluency, and ease of reading.

- 1: Frequent grammar or readability problems seriously affect understanding.
- 2: Several language issues make parts of the answer difficult to read.
- 3: The answer is generally understandable but contains noticeable language issues.
- 4: The answer is fluent and readable with only minor language issues.
- 5: The answer is fluent, clear, grammatically accurate, and easy to read.

### 12.7 Primary Metrics

本项目只设置 primary metrics。它们直接对应 Evaluator Agent 的 rubric scores，用于衡量最终文本质量。

#### Overall Score

综合质量分数，表示文本在所有评价维度上的整体表现。

默认计算方式：

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

如果 Evaluator 同时输出了 `overall_score`，系统仍应根据各维度分数重新计算一次，用于保证一致性。

#### Relevance

衡量文本是否直接回应写作任务，是否覆盖 instruction 中的核心要求。

#### Structure

衡量文本的组织结构、段落安排、逻辑顺序和整体连贯性。

#### Evidence Use

衡量文本是否准确、具体、有效地使用 source material 或背景信息支持论点。

#### Argument Clarity

衡量中心论点是否明确，推理是否清楚，是否体现基本的批判性思考。

#### Academic Style

衡量文本语言是否正式、客观、准确，是否符合学术写作风格。

#### Grammar and Readability

衡量文本是否语法准确、表达流畅、易于阅读。

### 12.8 Evaluator Output Schema

Evaluator 必须输出可解析 JSON，不应输出 Markdown 或额外解释文字。

推荐格式：

```json
{
  "eval_id": "E0001",
  "scores": {
    "relevance": 4,
    "structure": 5,
    "evidence_use": 4,
    "argument_clarity": 4,
    "academic_style": 5,
    "grammar_readability": 5
  },
  "overall_score": 4.5,
  "justification": "The answer is relevant, well structured, and written in an academic tone, though evidence use could be more specific."
}
```

字段约束：

- 所有 score 必须是 1-5 的整数。
- `overall_score` 必须是 1-5 的数字。
- `justification` 应简短，不超过 80 words。
- 输出必须能被 JSON parser 直接解析。

如果 JSON 解析失败：

1. 进行一次 repair prompt。
2. 如果仍失败，将该 evaluation 标记为 `parse_failed`。
3. 不应手动猜测分数。

### 12.9 Evaluator Prompt Template

Evaluator prompt 应保持固定。示例：

```text
You are an independent academic writing evaluator.

Evaluate the answer according to the given writing task, source material, target word count, and rubric.

You must not assume anything about how the answer was generated.
You must not reward or penalize the answer based on any workflow.
Evaluate only the quality of the final answer.

Use a 1-5 integer scale for each dimension:
1 = very poor
2 = weak
3 = acceptable
4 = good
5 = excellent

Return only valid JSON with the following fields:
eval_id, scores, overall_score, justification.

Writing task:
{instruction}

Source material:
{source_material}

Target word count:
{target_word_count}

Rubric:
{rubric}

Answer:
{answer}
```

### 12.10 Statistical Analysis

由于同一任务会在多个 conditions 下运行，本项目采用 paired comparison。

推荐分析流程：

1. 对每个 `task_id + condition` 聚合 3 次 repetitions。
2. 计算每个 condition 在每个 task 上的 mean overall score。
3. 使用 task-level paired comparison 比较 conditions。

主要比较：

- Condition B vs Condition A
- Condition C vs Condition A
- Condition C vs Condition B

报告内容：

- mean score
- standard deviation
- mean difference
- win / tie / loss count
- win rate
- optional p-value

统计检验建议：

- 如果样本量约 20，优先使用 Wilcoxon signed-rank test。
- paired t-test 可作为补充，但不作为唯一证据。
- coursework 中可以把统计检验作为 supporting evidence，而不是过度强调显著性。

Effect size 建议报告：

```text
mean_difference = mean(score_condition_x - score_condition_y)
```

如时间允许，可额外报告 Cohen's d for paired samples。

### 12.11 Stability Analysis

稳定性通过同一 task、同一 condition 的多次 repetitions 计算。

可记录：

- per-task score standard deviation
- per-condition average standard deviation
- coefficient of variation，可选

如果某个 workflow 平均分更高但方差也明显更高，应在 report 中说明其稳定性风险。

### 12.12 Cost and Runtime Analysis

虽然 cost 和 runtime 不作为 primary metrics，但仍应作为实验代价记录和讨论。

每次 run 应记录：

```json
{
  "task_id": "T001",
  "condition": "plan_execute_critique",
  "repetition_id": 1,
  "runtime_seconds": 42.3,
  "input_tokens": 3200,
  "output_tokens": 1100,
  "total_tokens": 4300,
  "estimated_cost": 0.012
}
```

如果 API provider 不返回 token usage，MVP 可以先记录 runtime，并将 token/cost 标记为 optional。不要为了 token 统计引入过多复杂依赖。

成本分析重点不是精确到真实账单，而是比较不同 workflow 的相对开销。

### 12.13 Result Files

正式实验至少保存以下文件：

```text
results/
  runs.jsonl
  evaluation_items.jsonl
  evaluation_results.jsonl
  scores.csv
  summary.csv
  charts/
    mean_scores.png
    score_distribution.png
```

`runs.jsonl` 保存完整 generation trace，包括 plan、draft、critique、final answer、runtime 和模型配置。

`evaluation_items.jsonl` 保存匿名评分输入。

`evaluation_results.jsonl` 保存 evaluator 原始评分输出。

`scores.csv` 保存扁平化后的分数，便于 pandas 分析。

`summary.csv` 保存 condition-level 聚合结果。

### 12.14 Minimum Acceptable Evaluation for Coursework

考虑项目复杂度和 coursework 时间，MVP 最低应完成：

1. 至少 20 个正式 writing tasks。
2. 至少 3 个实验条件：Baseline、Plan-Execute、Plan-Execute-Critique。
3. 每个 condition 至少重复 3 次。
4. Evaluator 使用固定 prompt 和固定 temperature。
5. Final answers 匿名化后评分。
6. 保存完整 generation trace 和 evaluation result。
7. 输出 mean score、standard deviation、win rate。
8. 生成平均分柱状图和分数分布图。
9. 在 report 中讨论 LLM-as-judge 的限制。

### 12.15 Limitations

本评估方案存在以下限制：

- Evaluator Agent 本身可能存在偏差。
- LLM-as-judge 不等同于人工专家评分。
- 小规模任务集不能证明系统在所有学术写作任务中都有效。
- 不同模型、temperature 和 prompt 可能影响结果。
- Multi-agent workflow 的提升可能来自更长上下文处理和更多 token，而不完全来自 agent 协作本身。

因此，实验结论应表述为：

> 在本项目设定的任务集、模型配置和评分协议下，某个 multi-agent workflow 相比 baseline 表现出更高/更稳定/更昂贵的趋势。

而不应表述为：

> Multi-agent writing systems 普遍优于 single-agent systems.

---

## 13. Dataset 设计

建议自建小型数据集，避免伦理和隐私问题。

推荐规模：

- 5 个任务用于 prompt debugging。
- 20-50 个任务用于正式实验。

每条数据格式：

```json
{
  "task_id": "T001",
  "instruction": "Write a 250-word critical paragraph about the benefits and limitations of AI-assisted academic writing.",
  "source_material": "Short background notes or open-access material.",
  "target_word_count": 250,
  "rubric": {
    "relevance": 5,
    "structure": 5,
    "evidence_use": 5,
    "academic_style": 5,
    "clarity": 5
  }
}
```

数据集准备原则：
- 不使用真实学生作文。
- 不收集真实用户交互数据。
- 尽量使用自己编写的题目和短背景材料。
- 可以使用 public-domain 或 open-access 材料。
- 每个 source material 控制在较短长度，降低 API 成本。
- 任务主题覆盖多个学术方向，减少单一主题偏差。

---

## 14. 技术栈

推荐技术栈：
- **Python**：  
- **CrewAI**：轻量级 multi-agent 编排框架，用于定义 Agent、Task、Crew 和 sequential workflow。
- **OpenAI-compatible API client**：调用外部 LLM。
- **YAML / dotenv**：配置管理和 API key 管理。
- **Pydantic**：定义结构化 agent 输出和 evaluation result。
- **JSONL / CSV**：保存实验日志和统计结果。
- **Pandas**：聚合实验结果。
- **Matplotlib / Seaborn**：生成图表。
- **pytest**：测试配置读取、数据加载、评分解析和 workflow。
- **Jupyter Notebook**：可选，用于实验结果分析。

选择 CrewAI 的原因：

- 它直接提供 Agent、Task、Crew 和 Process 抽象，和本项目的 planner、writer、critic、editor 工作流高度匹配。
- 支持 sequential process，适合 Plan-Execute 和 Plan-Execute-Critique。
- 相比 LangGraph 更容易上手，相比 AutoGen 更轻量。
- 可以减少手写 agent 编排代码，但仍允许保留 Python Experiment Runner 来控制实验条件、日志和评估。

不建议默认使用复杂框架，例如 AutoGen 或 LangGraph。除非后期需要更复杂的状态图、工具调用或 agent 对话机制，否则 CrewAI 更适合本项目的 lightweight 目标。

## 15. CrewAI 使用方式

CrewAI 用于实现生成阶段的 multi-agent workflow。推荐将 Evaluator 作为独立评分器，而不是混入被比较的生成 Crew 中。

推荐结构：

```text
Python Experiment Runner
        |
        v
CrewAI Generation Crew
        |
        v
Planner Agent -> Writer Agent -> Critic Agent -> Editor Agent
        |
        v
Independent Evaluator Agent
```

不同实验条件的 CrewAI 映射：

- **Condition A：Single-Agent Baseline**
  - 一个 Writer Agent。
  - 一个直接写作 Task。
- **Condition B：Plan-Execute**
  - Planner Agent + Writer Agent。
  - 使用 sequential process。
- **Condition C：Plan-Execute-Critique**
  - Planner Agent + Writer Agent + Critic Agent + Editor Agent。
  - 使用 sequential process。
- **Condition D：Multi-Critic，可选**
  - Planner Agent + Writer Agent + Structure Critic + Evidence Critic + Style Critic + Editor Agent。
  - Editor 汇总多个 critic 的反馈后生成最终文本。

Evaluator 的设计原则：

- Evaluator 可以实现为单独的 CrewAI Agent，也可以通过统一 `llm_client` 直接调用。
- Evaluator 不参与 generation crew。
- 所有 condition 使用同一个 Evaluator 配置评分。
- Evaluator 不知道文本来自哪个 condition。

## 16. 推荐代码模块

建议项目结构：

```text
src/
  config.py
  llm_client.py
  environment.py
  orchestrator.py
  crew_factory.py
  agents/
    planner.py
    writer.py
    critic.py
    editor.py
    evaluator.py
  experiments/
    runner.py
    analyze.py
data/
  tasks_debug.jsonl
  tasks_main.jsonl
configs/
  config.yaml
results/
  runs.jsonl
  scores.csv
  charts/
```

模块职责：

- `config.py`：读取 config.yaml 和环境变量。
- `llm_client.py`：统一封装外部 LLM API 调用，供 Evaluator 或非 CrewAI 调用使用。
- `environment.py`：定义 writing environment 和 shared workspace。
- `orchestrator.py`：根据实验 condition 调用不同 CrewAI workflow。
- `crew_factory.py`：创建 CrewAI agents、tasks 和 crews。
- `agents/`：集中管理不同 agent 的 prompt、role、goal 和 expected output。
- `experiments/runner.py`：批量运行任务和重复实验。
- `experiments/analyze.py`：聚合结果并生成图表。

## 17. 最小可行版本

最小可行版本需要实现：

1. 读取配置文件和 API key。
2. 读取 JSONL 写作任务。
3. 使用 CrewAI 实现 Single-Agent Baseline。
4. 使用 CrewAI 实现 Plan-Execute workflow。
5. 使用 CrewAI 实现 Plan-Execute-Critique workflow。
6. 保存每次运行的完整输出。
7. 使用独立 Evaluator Agent 输出 JSON 分数。
8. 聚合结果到 CSV。
9. 生成至少两类图表：
   - 平均分对比图
   - 分数分布图
