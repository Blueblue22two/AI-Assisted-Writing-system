# Multi-Agent Academic Writing Assistant

## Overview

This project is a lightweight multi-agent academic writing experiment system for coursework. The main goal is to compare different workflows (single-agent vs multi-agent) under the same tasks and rubric, focusing on output quality and stability.

The current implementation uses **Centralized Orchestrator + CrewAI**:

- `single_agent`: Writer
- `plan_execute`: Planner -> Writer
- `plan_execute_critique`: Planner -> Writer -> Critic -> Editor
- An independent `EvaluatorAgent` scores final outputs (not part of generation workflows)

## Implemented Features

- Load configuration and secrets from `configs/config.yaml` + `.env` (with Pydantic validation).
- Load and strictly validate task datasets from JSONL.
- Run 3 experimental conditions (A/B/C).
- Save each run to `results/runs.jsonl` (including dimension scores, overall score, runtime, model info).
- Generate anonymized evaluation inputs in `results/evaluation_items.jsonl`.
- Analysis script outputs:
  - `results/scores.csv`
  - `results/condition_summary.csv`
  - `results/win_rates.csv`
  - `results/mean_scores.png`
  - `results/score_distribution.png`
  - `results/detailed_metrics.png`
  - `results/runtime.png`

## Data and Rubric Schema

Single task item example (JSONL):

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

`rubric` must contain exactly these 6 primary metrics.

## Configuration (Current Defaults)

Current `configs/config.yaml`:

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

`.env` (do not commit real keys):

```env
LLM_API_KEY=your_api_key_here
EVALUATOR_API_KEY=your_evaluator_api_key_here
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.experiments.runner --config configs/config.yaml --tasks data/tasks_main.jsonl
python -m src.experiments.analyze --results results/runs.jsonl --output-dir results
```

Debug mode (automatically uses `data/tasks_debug.jsonl` and sets repetitions to 1):

```bash
python -m src.experiments.runner --debug
```

## Project Structure

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

## Documentation

- `README.md`: English default quick-start and current implementation status.
- `README_CN.md`: Chinese version of this README.
