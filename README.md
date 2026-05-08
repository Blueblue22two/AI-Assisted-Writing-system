# Multi-Agent Academic Writing Assistant

## 项目目标

本项目构建一个轻量级 Multi-Agent 学术写作辅助系统，用于完成 Multi-Agent System 方向的 coursework。系统的目标不是开发生产级写作产品，而是设计一个可实验评估的 agent-based system，用来研究结构化多智能体协作是否相比单智能体写作提升文本质量。

核心研究问题：

> 在相同写作任务、参考材料和评分标准下，轻量级 multi-agent plan-execute 写作系统是否比 single-agent baseline 生成质量更高、更稳定的学术文本？

## 1. Multi-Agent System Design

本项目采用 **Centralized Orchestrator + Shared Workspace** 架构，并使用 **CrewAI** 作为轻量级 multi-agent 编排框架。

- **Orchestrator**：确定性的 Python workflow controller，不是 LLM-based Agent。
- **CrewAI**：用于定义 `Agent`、`Task`、`Crew` 和 sequential workflow。
- **Shared Workspace**：保存 task、source material、plan、draft、critique、final answer、evaluation result 和运行日志。
- **Agents**：负责规划、写作、批评、编辑和评分。

核心范式：**Plan-Execute**

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

Evaluator 建议作为独立评分器，不混入被比较的 generation crew。这样实验比较的是不同写作 workflow，而不是评分器本身。

## 2. Agents

系统包含以下 agents：

1. **Planner Agent**
   理解任务要求，生成中心论点、段落结构、关键论点和证据使用计划。
2. **Writer Agent**
   根据 Planner Agent 的计划和参考材料生成 academic draft。
3. **Critic Agent**
   根据 rubric 批评文本，重点检查结构、逻辑、证据使用、清晰度和学术风格。
4. **Editor Agent**
   根据 Critic Agent 的反馈修订文本，输出 final answer。
5. **Evaluator Agent**
   根据固定 rubric 对最终文本评分，输出结构化 JSON 分数。该 agent 可以使用不同于生成类 agents 的 LLM，以提高评分稳定性和减少自评偏差。

可选扩展：

- Structure Critic Agent
- Evidence Critic Agent
- Style Critic Agent

## 3. 功能

最小可行版本计划实现：

- 读取 JSONL 格式的写作任务数据集。
- 读取 `config.yaml` 和 `.env` 中的模型/API 配置。
- 使用 CrewAI 实现 Single-Agent Baseline。
- 使用 CrewAI 实现 Plan-Execute workflow。
- 使用 CrewAI 实现 Plan-Execute-Critique workflow。
- 调用独立 Evaluator Agent 进行 rubric-based evaluation。
- 保存每次运行的完整 agent trace、最终文本、评分、token usage 和 runtime。
- 聚合结果到 CSV。
- 生成平均分对比图和分数分布图。

实验条件：

- **Condition A: Single-Agent Baseline**
  一个 LLM 直接根据 task、source material 和 rubric 生成最终文本。
- **Condition B: Plan-Execute**
  Planner Agent 先生成计划，Writer Agent 再写作。
- **Condition C: Plan-Execute-Critique**
  Planner Agent -> Writer Agent -> Critic Agent -> Editor Agent。
- **Condition D: Multi-Critic，可选**
  多个 critic 分别从结构、证据和风格角度评价初稿，Editor Agent 综合反馈后修订。

---

## 4. 技术栈

推荐技术栈：

- **Python**：
- **CrewAI**：轻量级 multi-agent 编排框架。
- **OpenAI-compatible API client**：调用外部 LLM API。
- **YAML / dotenv**：配置管理和 API key 管理。
- **Pydantic**：定义结构化输出和 evaluation result。
- **JSONL / CSV**：保存任务数据、运行日志和评分结果。
- **Pandas**：聚合实验结果。
- **Matplotlib / Seaborn**：生成可视化图表。
- **pytest**：测试配置读取、数据加载、评分解析和 workflow。
- **Jupyter Notebook**：可选，用于结果分析。

模型建议：

- 生成类 agents 默认使用同一模型 `deepseek-v4-flash`，以保持实验公平和成本可控。
- Evaluator Agent 推荐使用更强或更稳定的独立模型，例如 `gpt-5.2`。
- Evaluator temperature 固定为 `0.0`。
- Planner / Critic temperature 可设为 `0.2-0.3`。
- Writer / Editor temperature 可设为 `0.3-0.6`。


---

## 5. 配置管理
所有 LLM 调用都使用外部 API key。API key 不写入代码、不写入日志、不提交到仓库。
`.env` 示例：

```env
LLM_API_KEY=your_api_key_here
EVALUATOR_API_KEY=your_evaluator_api_key_here
```

`configs/config.yaml` 示例：

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
---

## 6. Evaluation

本项目使用独立 Evaluator Agent 进行 rubric-based evaluation。Evaluator Agent 不参与文本生成 workflow，只负责对各 condition 生成的 final answer 进行统一评分。

为了降低评分偏差，Evaluator 不应知道答案来自哪个 condition，也不应看到 plan、draft、critique 或 agent workflow。正式评估时，final answer 会先转换为匿名 evaluation item。

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

### Primary Metrics

本项目只设置 primary metrics。它们直接对应 Evaluator Agent 的 rubric scores，用于衡量最终文本质量。

1. **overall score**
   综合质量分数，表示文本在所有评价维度上的整体表现。
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
2. **relevance**
   衡量文本是否直接回应写作任务，是否覆盖 instruction 中的核心要求。
3. **structure**
   衡量文本的组织结构、段落安排、逻辑顺序和整体连贯性。
4. **evidence use**
   衡量文本是否准确、具体、有效地使用 source material 或背景信息支持论点。
5. **argument clarity**
   衡量中心论点是否明确，推理是否清楚，是否体现基本的批判性思考。
6. **academic style**
   衡量文本语言是否正式、客观、准确，是否符合学术写作风格。
7. **grammar and readability**
   衡量文本是否语法准确、表达流畅、易于阅读。

### Evaluation Method
- 使用固定 rubric 和固定 Evaluator prompt。
- Evaluator 输出 JSON，便于自动统计。
- Evaluator 不知道文本来自哪个 condition。
- 每个任务在每个 condition 下重复运行多次。
- 对不同 condition 的平均分、标准差和分布进行比较。
- 可选使用 paired t-test 或 Wilcoxon signed-rank test。

推荐实验数据：

- 5 个任务用于 prompt debugging。
- 20-50 个任务用于正式实验。
- 每条任务包含 instruction、source material、target word count 和 rubric。
- 不使用真实学生作文，避免隐私和 ethics 风险。

任务数据示例：

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

***

---

## 7. 推荐项目结构

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

***

## 8. 如何部署和运行

当前仓库已经包含推荐项目结构、配置样例、任务样例和依赖文件。首次部署时按以下步骤操作。

#### 1. 创建虚拟环境。  

在项目根目录运行：

```bash
python -m venv .venv
```

这会在项目根目录创建一个 `.venv/` 文件夹，用来隔离本项目依赖，避免污染系统 Python 环境。

#### 2. 激活虚拟环境。  
macOS / Linux：
```bash
source .venv/bin/activate
```

Windows PowerShell：
```bash
.venv\Scripts\Activate.ps1
```

Windows Command Prompt：
```bash
.venv\Scripts\activate.bat
```
激活成功后，终端提示符前通常会出现 `(.venv)`。

- 如需退出虚拟环境：  
```bash
deactivate
```

#### 3. 安装依赖。  
确保虚拟环境已激活，然后运行：
```bash
pip install -r requirements.txt
```

#### 4. 创建 `.env`。  
   在项目根目录创建 `.env` 文件，并写入 API key（此时已默认创建并且填写，不要改动）：

```bash
LLM_API_KEY=your_api_key_here
EVALUATOR_API_KEY=your_evaluator_api_key_here
```
注意：`.env` 中不能写入真实 coursework 文档或公开仓库。

#### 5. 编辑配置文件。  
打开 `configs/config.yaml`，根据实际 API 服务填写（默认已填写，不用管）：

- `base_url`
- `default_model`
- `model`
- `temperature`
- `max_tokens`
- `repetitions`

默认生成类模型示例为 `deepseek-v4-flash`，Evaluator 示例为 `gpt-5.2`。实际使用时可以替换为你有权限调用的模型。


#### 6. 准备任务数据。  
   仓库已提供两个样例文件：
- `data/tasks_debug.jsonl`：用于 prompt 和流程调试。
- `data/tasks_main.jsonl`：用于正式实验，可继续扩充到 20-50 条任务。

  <br />


#### （**以下步骤需要在代码实现完成后执行**）

#### 7. 运行实验。  
   代码实现完成后，可以使用以下命令运行主实验：

```bash
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
```

#### 8. 聚合和可视化结果。  

```bash
python -m src.experiments.analyze --results results/runs.jsonl
```

