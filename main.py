"""
Main entry point for the Multi-Agent Academic Writing Assistant.
Usage: python main.py --mode [debug|full]
"""

import argparse
import sys
from pathlib import Path

# Add src to path if running from project root
sys.path.insert(0, str(Path(__file__).parent))

from src.experiments.runner import ExperimentRunner


def main() -> None:
    """Parse arguments and run the appropriate experiment mode."""
    parser = argparse.ArgumentParser(
        description="Run Multi-Agent Academic Writing Assistant experiments"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["debug", "full"],
        default="debug",
        help="Experiment mode: debug (1 task, 1 rep) or full (all tasks, all reps)",
    )
    parser.add_argument(
        "--tasks",
        type=str,
        default="data/tasks_debug.jsonl",
        help="Path to tasks JSONL file",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=3,
        help="Number of repetitions per condition (full mode only)",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="Maximum number of tasks to process (overrides full mode)",
    )

    args = parser.parse_args()

    runner = ExperimentRunner()

    if args.mode == "debug":
        # Use debug tasks file if not specified
        tasks_path = args.tasks if args.tasks != "data/tasks_debug.jsonl" else "data/tasks_debug.jsonl"
        runner.run_debug(tasks_path)
    else:  # full mode
        # Use main tasks file by default
        tasks_path = args.tasks if args.tasks != "data/tasks_debug.jsonl" else "data/tasks_main.jsonl"
        runner.run_experiment(
            tasks_path=tasks_path,
            conditions=["baseline", "plan_execute", "plan_execute_critique"],
            repetitions=args.repetitions,
            max_tasks=args.max_tasks,
        )


if __name__ == "__main__":
    main()