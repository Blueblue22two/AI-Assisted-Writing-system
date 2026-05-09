"""补跑缺失的实验运行。

此脚本仅重新运行 runs.jsonl 中缺失的 (task_id, condition, repetition_id) 组合，
不会重复运行已有记录。
"""

import json
import logging
import sys
from pathlib import Path

# 明确缺失的 15 个组合
MISSING_RUNS = [
    ("T003", "plan_execute",           1),
    ("T004", "plan_execute_critique",  2),
    ("T006", "plan_execute_critique",  1),
    ("T008", "plan_execute",           1),
    ("T008", "plan_execute_critique",  1),
    ("T010", "plan_execute",           1),
    ("T010", "plan_execute",           2),
    ("T011", "plan_execute",           2),
    ("T012", "plan_execute_critique",  3),
    ("T014", "plan_execute_critique",  1),
    ("T015", "plan_execute",           1),
    ("T018", "plan_execute",           3),
    ("T019", "plan_execute_critique",  1),
    ("T023", "plan_execute",           2),
    ("T025", "plan_execute_critique",  3),
]


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("experiment.log"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger(__name__)

    from src.config import load_config, load_tasks_jsonl
    from src.orchestrator import Orchestrator

    logger.info("=== 补跑缺失实验 ===")
    logger.info(f"共需补跑 {len(MISSING_RUNS)} 个运行")

    config, secrets = load_config("configs/config.yaml")
    all_tasks = load_tasks_jsonl("data/tasks_main.jsonl")
    task_map = {t.task_id: t for t in all_tasks}

    orchestrator = Orchestrator(config, secrets)

    success_count = 0
    fail_count = 0

    for i, (task_id, condition, rep) in enumerate(MISSING_RUNS, 1):
        task = task_map.get(task_id)
        if task is None:
            logger.error(f"[{i}/{len(MISSING_RUNS)}] ❌ 找不到任务: {task_id}")
            fail_count += 1
            continue

        logger.info(f"[{i}/{len(MISSING_RUNS)}] 🚀 补跑: task={task_id}, condition={condition}, rep={rep}")
        try:
            result = orchestrator.run_single_condition(task, condition, rep)
            logger.info(
                f"[{i}/{len(MISSING_RUNS)}] ✅ 完成: task={task_id}, condition={condition}, "
                f"rep={rep}, score={result['evaluation']['overall_score']:.2f}"
            )
            success_count += 1
        except Exception as exc:
            logger.error(f"[{i}/{len(MISSING_RUNS)}] ❌ 失败: task={task_id}, condition={condition}, rep={rep}: {exc}")
            fail_count += 1

    logger.info("=== 补跑完成 ===")
    logger.info(f"成功: {success_count} / {len(MISSING_RUNS)}")
    logger.info(f"失败: {fail_count} / {len(MISSING_RUNS)}")

    if fail_count > 0:
        logger.warning("有部分运行仍然失败，请检查 experiment.log 并手动重试")
        sys.exit(1)


if __name__ == "__main__":
    main()
