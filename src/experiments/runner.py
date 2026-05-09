"""CLI entry point for running writing experiments."""

import argparse
import logging
import sys

from src.config import load_config, load_tasks_jsonl
from src.orchestrator import Orchestrator


def main():
    """Main entry point for running experiments."""
    parser = argparse.ArgumentParser(description="Run academic writing experiments")
    parser.add_argument(
        "--config",
        default="configs/config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--tasks",
        default="data/tasks_main.jsonl",
        help="Path to tasks JSONL file"
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=None,
        help="Number of repetitions per condition (overrides config)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Run in debug mode with fewer tasks"
    )
    parser.add_argument(
        "--debug-tasks",
        default="data/tasks_debug.jsonl",
        help="Path to debug tasks JSONL file"
    )
    
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("experiment.log"),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)

    try:
        logger.info("Loading configuration")
        config, secrets = load_config(args.config)

        if args.debug:
            logger.info("Running in debug mode")
            tasks = load_tasks_jsonl(args.debug_tasks)
            n_repetitions = 1
        else:
            tasks = load_tasks_jsonl(args.tasks)
            n_repetitions = args.repetitions or config.experiment.repetitions

        logger.info(f"Loaded {len(tasks)} tasks")
        logger.info(f"Running {n_repetitions} repetitions per condition")

        orchestrator = Orchestrator(config, secrets)

        logger.info("Starting experiment runs")
        results = orchestrator.run_all_tasks(tasks, n_repetitions)

        logger.info(f"Completed {len(results)} runs")

        orchestrator.generate_evaluation_items(tasks)
        logger.info("Generated evaluation items")

        logger.info("Experiment completed successfully")

    except Exception as exc:
        logger.error(f"Experiment failed: {exc}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()