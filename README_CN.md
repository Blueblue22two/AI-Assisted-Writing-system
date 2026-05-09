# Multi-Agent Academic Writing Assistant

## 项目简介

本项目是一个用于 coursework 的轻量级多智能体学术写作实验系统。核心目标是比较不同 workflow（single-agent vs multi-agent）在同一任务与评分标准下的输出质量与稳定性。

当前实现采用 **Centralized Orchestrator + CrewAI**：

- `single_agent`：Writer
- `plan_execute`：Planner -> Writer
- `plan_execute_critique`：Planner -> Writer -> Critic -> Editor
- 独立 `EvaluatorAgent` 对最终答案统一评分（不参与生成流程）

## 技术栈

- Python
- CrewAI
- OpenAI-compatible API 调用
- Pydantic
- YAML + dotenv
- JSONL / CSV
- Pandas
- Matplotlib / Seaborn
- pytest

## Agents

系统包含以下 agents：

- **Planner Agent**：理解任务要求，生成中心论点、段落结构、关键论点和证据使用计划。
- **Writer Agent**：根据 Planner Agent 的计划和参考材料生成 academic draft。
- **Critic Agent**：根据 rubric 批评文本，重点检查结构、逻辑、证据使用、清晰度和学术风格。
- **Editor Agent**：根据 Critic Agent 的反馈修订文本，输出 final answer。
- **Evaluator Agent**：根据固定 rubric 对最终文本评分，输出结构化 JSON 分数。该 agent 可以使用不同于生成类 agents 的 LLM，以提高评分稳定性和减少自评偏差。

## 当前已实现能力

- 从 `configs/config.yaml` + `.env` 加载配置与密钥（Pydantic 校验）。
- 从 JSONL 加载任务并严格校验 schema。
- 运行 3 个实验条件（A/B/C）。
- 每次 run 写入 `results/runs.jsonl`（含分维度分数、overall、runtime、model_info）。
- 生成匿名评估输入 `results/evaluation_items.jsonl`。
- 分析脚本输出：
  - `results/scores.csv`
  - `results/condition_summary.csv`
  - `results/win_rates.csv`
  - `results/mean_scores.png`
  - `results/score_distribution.png`
  - `results/detailed_metrics.png`
  - `results/runtime.png`

## 数据与评分字段（与代码一致）

任务 JSONL 单条示例：

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
    "argument_clarity": 5,
    "academic_style": 5,
    "grammar_readability": 5
  }
}
```

`rubric` 必须且仅可包含以上 6 个主指标。

## 配置（当前仓库默认值）

`configs/config.yaml` 当前示例：

```yaml
llm:
  provider: "openai-compatible"
  base_url: "https://api.deepseek.com/v1"
  api_key_env: "LLM_API_KEY"
  default_model: "deepseek-chat"
  temperature: 0.4
  max_tokens: 4000

evaluator_llm:
  provider: "openai-compatible"
  base_url: "https://api.deepseek.com/v1"
  api_key_env: "EVALUATOR_API_KEY"
  model: "deepseek-reasoner"
  temperature: 0.0
  max_tokens: 4000

experiment:
  repetitions: 1
  output_dir: "results"
```

`.env`（不提交真实密钥）：

```env
LLM_API_KEY=your_api_key_here
EVALUATOR_API_KEY=your_evaluator_api_key_here
```

## 快速运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
python -m src.experiments.analyze --results results/runs.jsonl --output-dir results
```

调试模式（自动使用 `data/tasks_debug.jsonl`，并将 repetitions 设为 1）：

```bash
python -m src.experiments.runner --debug
```

## 项目结构

```text
src/
  config.py
  llm_client.py
  environment.py
  orchestrator.py
  crew_factory.py
  agents/
  experiments/
data/
configs/
results/
tests/
tools/
docs/
```

## 文档说明

- `README.md`：英文默认版，面向快速使用和当前实现状态。
- `README_CN.md`：中文版本。
