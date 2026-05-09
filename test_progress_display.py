"""Test script to demonstrate progress display with mock runs."""

import logging
import time
from pathlib import Path

from tqdm import tqdm

# 模拟日志输出
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def simulate_experiment():
    """Simulate a small experiment to show progress display."""

    # 模拟实验参数
    n_tasks = 3
    n_conditions = 3
    n_repetitions = 2
    total_runs = n_tasks * n_conditions * n_repetitions

    print("\n" + "="*70)
    print("📊 实验进度显示演示")
    print("="*70)
    print(f"任务数量: {n_tasks}")
    print(f"实验条件: {n_conditions} (single_agent, plan_execute, plan_execute_critique)")
    print(f"每条件重复次数: {n_repetitions}")
    print(f"总运行次数: {total_runs}")
    print("="*70 + "\n")

    conditions = ["single_agent", "plan_execute", "plan_execute_critique"]
    tasks = [f"T{i:03d}" for i in range(1, n_tasks + 1)]

    completed_runs = 0

    for i, task_id in enumerate(tqdm(tasks, desc="Overall Progress", unit="task"), 1):
        logger.info(f"📋 Starting task {task_id} ({i}/{n_tasks})")

        task_completed = 0
        for condition in conditions:
            for rep in range(1, n_repetitions + 1):
                logger.info(f"🚀 Starting: task={task_id}, condition={condition}, rep={rep}/{n_repetitions}")

                # 模拟 API 调用和处理时间
                time.sleep(0.3)

                # 模拟评分
                score = 4.5 + (i * 0.1)

                logger.info(f"✅ Completed: task={task_id}, condition={condition}, rep={rep}, score={score:.2f}")

                completed_runs += 1
                task_completed += 1

        logger.info(f"📊 Task {task_id} completed: {task_completed} runs")
        logger.info(f"Progress: {completed_runs}/{total_runs} runs completed ({completed_runs/total_runs*100:.1f}%)\n")

    print("\n" + "="*70)
    print(f"✅ 实验完成！总共完成 {completed_runs} 次运行")
    print("="*70)


if __name__ == "__main__":
    simulate_experiment()
