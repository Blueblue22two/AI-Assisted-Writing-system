"""
Experiment runner for batch execution of tasks across conditions and repetitions.
Saves all intermediate outputs and results.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import get_config
from src.environment import SharedWorkspace
from src.orchestrator import Orchestrator


class ExperimentRunner:
    """
    Runs multiple tasks across experimental conditions with repetitions.
    Saves results to JSONL files for later analysis.
    """

    def __init__(self, output_dir: str = "results") -> None:
        """
        Initialize the experiment runner.

        Args:
            output_dir: Directory where results will be saved.
        """
        self.config = get_config()
        self.orchestrator = Orchestrator()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.runs_dir = self.output_dir / "runs"
        self.runs_dir.mkdir(exist_ok=True)

        # File handles for streaming writes
        self.runs_file = None  # Will be opened later

    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _save_run(self, workspace: SharedWorkspace) -> None:
        """Append a single run result to the JSONL file."""
        with open(self.runs_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(workspace.to_dict(), ensure_ascii=False) + "\n")

    def load_tasks(self, tasks_path: str) -> List[Dict[str, Any]]:
        """
        Load tasks from a JSONL file.

        Args:
            tasks_path: Path to JSONL file containing tasks.

        Returns:
            List of task dictionaries.
        """
        tasks = []
        path = Path(tasks_path)
        if not path.exists():
            raise FileNotFoundError(f"Tasks file not found: {tasks_path}")

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    tasks.append(json.loads(line))

        return tasks

    def run_experiment(
        self,
        tasks_path: str,
        conditions: List[str],
        repetitions: int,
        max_tasks: Optional[int] = None,
    ) -> str:
        """
        Run the full experiment.

        Args:
            tasks_path: Path to the tasks JSONL file.
            conditions: List of condition names to run.
            repetitions: Number of times to repeat each condition per task.
            max_tasks: Optional limit on number of tasks to process.

        Returns:
            Path to the runs output file.
        """
        tasks = self.load_tasks(tasks_path)
        if max_tasks:
            tasks = tasks[:max_tasks]

        # Create output file with timestamp
        timestamp = self._get_timestamp()
        self.runs_file = self.runs_dir / f"runs_{timestamp}.jsonl"

        print(f"Starting experiment with {len(tasks)} tasks, {len(conditions)} conditions, {repetitions} repetitions each")

        total_runs = len(tasks) * len(conditions) * repetitions
        run_count = 0

        for task_idx, task in enumerate(tasks):
            print(f"\n--- Task {task_idx + 1}/{len(tasks)}: {task['task_id']} ---")

            for condition in conditions:
                for rep in range(repetitions):
                    run_count += 1
                    print(f"  Running {condition} repetition {rep + 1}/{repetitions} ({run_count}/{total_runs})")

                    # Create workspace for this run
                    workspace = SharedWorkspace.from_task_dict(task)
                    workspace.repetition_id = rep

                    # Run the condition
                    try:
                        workspace = self.orchestrator.run_condition(workspace, condition)
                        self._save_run(workspace)
                        print(f"    -> Done, overall_score: {workspace.evaluation['overall_score'] if workspace.evaluation else 'N/A'}")
                    except Exception as e:
                        print(f"    -> ERROR: {e}")
                        # Still save the failed run with error info
                        workspace.evaluation = {"error": str(e)}
                        self._save_run(workspace)

        print(f"\nExperiment complete. Results saved to {self.runs_file}")
        return str(self.runs_file)

    def run_debug(self, tasks_path: str) -> None:
        """
        Quick debug run with one task, one repetition per condition.

        Args:
            tasks_path: Path to debug tasks file.
        """
        print("=== DEBUG MODE ===")
        self.run_experiment(
            tasks_path=tasks_path,
            conditions=["baseline", "plan_execute", "plan_execute_critique"],
            repetitions=1,
            max_tasks=1,  # Only first task
        )