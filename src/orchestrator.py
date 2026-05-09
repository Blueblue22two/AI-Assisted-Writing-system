"""Experiment workflow orchestration across CrewAI conditions."""

import json
import logging
import uuid
from pathlib import Path
from typing import Optional

from src.agents.evaluator import EvaluatorAgent
from src.config import AppConfig, RuntimeLLMSecrets, WritingTask
from src.crew_factory import CrewFactory
from src.environment import EvaluationResult, WritingEnvironment
from src.llm_client import LLMClientFactory

logger = logging.getLogger(__name__)


class Orchestrator:
    """Central orchestrator for running writing experiments across conditions."""

    def __init__(self, config: AppConfig, secrets: RuntimeLLMSecrets):
        self.config = config
        self.secrets = secrets
        self.crew_factory = CrewFactory(config.llm, secrets.llm_api_key)
        self.evaluator_agent = self._create_evaluator()
        self.environment = WritingEnvironment()
        self._ensure_output_dir()

    def _create_evaluator(self) -> EvaluatorAgent:
        """Create the evaluator agent with its own LLM configuration."""
        client = LLMClientFactory.create_evaluator_client(self.config.evaluator_llm, self.secrets)
        return EvaluatorAgent(client)

    def _ensure_output_dir(self):
        """Ensure the output directory exists."""
        Path(self.config.experiment.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.experiment.output_dir, "charts").mkdir(parents=True, exist_ok=True)

    def run_single_condition(self, task: WritingTask, condition: str, repetition_id: int) -> dict:
        """
        Run a single task under a single experimental condition.
        
        Args:
            task: The writing task to execute
            condition: The experimental condition (single_agent, plan_execute, plan_execute_critique)
            repetition_id: The repetition number for this run
            
        Returns:
            Dictionary containing the complete run result
        """
        import time

        logger.info(f"Running task {task.task_id} under condition {condition} (repetition {repetition_id})")

        t_start = time.time()

        self.environment.setup_task(task, condition, repetition_id)

        crew = self.crew_factory.get_crew_for_condition(condition, task)

        try:
            result = crew.kickoff()
        except Exception as exc:
            logger.error(f"Crew execution failed: {exc}")
            raise

        t_end = time.time()
        runtime = t_end - t_start

        final_answer = str(result) if result else ""

        self.environment.execute_action("revise", final_answer=final_answer)

        eval_id = f"E{uuid.uuid4().hex[:8]}"
        evaluation = self.evaluator_agent.evaluate(
            eval_id=eval_id,
            instruction=task.instruction,
            source_material=task.source_material,
            target_word_count=task.target_word_count,
            rubric=task.rubric,
            answer=final_answer,
        )

        self.environment.execute_action("evaluate", evaluation=evaluation)

        self.environment.workspace.run_metadata.runtime_seconds = runtime
        self.environment.workspace.run_metadata.model_info = self.config.llm.default_model

        result_data = {
            "task_id": task.task_id,
            "condition": condition,
            "repetition_id": repetition_id,
            "run_id": f"R{uuid.uuid4().hex[:8]}",
            "eval_id": eval_id,
            "final_answer": final_answer,
            "evaluation": {
                "scores": evaluation.scores,
                "overall_score": evaluation.overall_score,
                "justification": evaluation.justification,
            },
            "runtime_seconds": runtime,
            "model_info": self.config.llm.default_model,
        }

        self._save_run_result(result_data)

        logger.info(f"Completed task {task.task_id} under condition {condition} - score: {evaluation.overall_score}")

        return result_data

    def _save_run_result(self, result_data: dict):
        """Save a single run result to the results JSONL file."""
        output_path = Path(self.config.experiment.output_dir, "runs.jsonl")
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result_data, ensure_ascii=False) + "\n")

    def run_task_conditions(self, task: WritingTask, repetitions: Optional[int] = None) -> list[dict]:
        """
        Run a single task across all experimental conditions.
        
        Args:
            task: The writing task to execute
            repetitions: Number of repetitions per condition (defaults to config value)
            
        Returns:
            List of all run results for this task
        """
        n_repetitions = repetitions or self.config.experiment.repetitions
        conditions = CrewFactory.list_conditions()
        all_results = []

        for condition in conditions:
            for rep in range(1, n_repetitions + 1):
                result = self.run_single_condition(task, condition, rep)
                all_results.append(result)

        return all_results

    def run_all_tasks(self, tasks: list[WritingTask], repetitions: Optional[int] = None) -> list[dict]:
        """
        Run all tasks across all experimental conditions.
        
        Args:
            tasks: List of writing tasks to execute
            repetitions: Number of repetitions per condition (defaults to config value)
            
        Returns:
            List of all run results
        """
        all_results = []

        for task in tasks:
            logger.info(f"Starting task {task.task_id}")
            task_results = self.run_task_conditions(task, repetitions)
            all_results.extend(task_results)
            logger.info(f"Completed task {task.task_id}: {len(task_results)} runs")

        return all_results

    def generate_evaluation_items(self, tasks: list[WritingTask]) -> list[dict]:
        """
        Generate anonymized evaluation items from runs.
        
        This is used for blind evaluation where the evaluator doesn't know
        which condition generated each answer.
        """
        runs_path = Path(self.config.experiment.output_dir, "runs.jsonl")
        if not runs_path.exists():
            logger.warning("No runs found to generate evaluation items from")
            return []

        evaluation_items = []
        seen_eval_ids = set()

        with open(runs_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    run = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if run["eval_id"] in seen_eval_ids:
                    continue
                seen_eval_ids.add(run["eval_id"])

                task = next((t for t in tasks if t.task_id == run["task_id"]), None)
                if not task:
                    continue

                item = {
                    "eval_id": run["eval_id"],
                    "task_id": run["task_id"],
                    "instruction": task.instruction,
                    "source_material": task.source_material,
                    "target_word_count": task.target_word_count,
                    "rubric": task.rubric.model_dump(),
                    "answer": run["final_answer"],
                }
                evaluation_items.append(item)

        output_path = Path(self.config.experiment.output_dir, "evaluation_items.jsonl")
        with open(output_path, "w", encoding="utf-8") as f:
            for item in evaluation_items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

        return evaluation_items