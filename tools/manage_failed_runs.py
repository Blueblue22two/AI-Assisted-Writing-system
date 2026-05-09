"""工具脚本：查看和管理失败的实验运行"""

import json
import argparse
from pathlib import Path
from collections import defaultdict


def analyze_failed_runs(runs_file: str = "results/runs.jsonl"):
    """分析失败的运行"""
    runs_path = Path(runs_file)

    if not runs_path.exists():
        print(f"❌ 文件不存在: {runs_file}")
        return

    failed_runs = []
    successful_runs = []

    with open(runs_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
                if run.get("status") == "failed":
                    failed_runs.append(run)
                else:
                    successful_runs.append(run)
            except json.JSONDecodeError:
                continue

    total_runs = len(failed_runs) + len(successful_runs)

    print("\n" + "="*70)
    print("📊 实验运行统计")
    print("="*70)
    print(f"总运行次数: {total_runs}")
    print(f"✅ 成功: {len(successful_runs)} ({len(successful_runs)/total_runs*100:.1f}%)")
    print(f"❌ 失败: {len(failed_runs)} ({len(failed_runs)/total_runs*100:.1f}%)")
    print("="*70)

    if not failed_runs:
        print("\n🎉 没有失败的运行！")
        return

    # 按错误类型分组
    error_types = defaultdict(list)
    for run in failed_runs:
        error_msg = run.get("error", "Unknown error")
        # 提取错误类型（取第一行）
        error_type = error_msg.split('\n')[0][:50]
        error_types[error_type].append(run)

    print(f"\n❌ 失败运行详情 ({len(failed_runs)} 次):")
    print("-"*70)

    for i, run in enumerate(failed_runs, 1):
        print(f"\n{i}. Task: {run['task_id']}, "
              f"Condition: {run['condition']}, "
              f"Rep: {run['repetition_id']}")
        print(f"   错误: {run.get('error', 'Unknown')[:100]}")

    print("\n" + "="*70)
    print("📋 按错误类型分组:")
    print("="*70)

    for error_type, runs in sorted(error_types.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n错误类型: {error_type}")
        print(f"出现次数: {len(runs)}")
        print(f"影响的运行:")
        for run in runs[:5]:  # 只显示前 5 个
            print(f"  - {run['task_id']}, {run['condition']}, rep {run['repetition_id']}")
        if len(runs) > 5:
            print(f"  ... 还有 {len(runs) - 5} 个")


def mark_failed_as_completed(runs_file: str = "results/runs.jsonl",
                             output_file: str = "results/runs_cleaned.jsonl"):
    """将失败的运行标记为已完成（跳过重试）"""
    runs_path = Path(runs_file)

    if not runs_path.exists():
        print(f"❌ 文件不存在: {runs_file}")
        return

    failed_count = 0

    with open(runs_path, "r", encoding="utf-8") as f_in, \
         open(output_file, "w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
                if run.get("status") == "failed":
                    # 移除 status 字段，使其看起来像成功的运行
                    run.pop("status", None)
                    # 添加占位数据
                    run["final_answer"] = "[FAILED - NO OUTPUT]"
                    run["evaluation"] = {
                        "scores": {k: 0.0 for k in ["relevance", "structure", "evidence_use",
                                                     "argument_clarity", "academic_style", "grammar_readability"]},
                        "overall_score": 0.0,
                        "justification": "Run failed, no evaluation performed"
                    }
                    run["runtime_seconds"] = 0.0
                    failed_count += 1

                f_out.write(json.dumps(run, ensure_ascii=False) + "\n")
            except json.JSONDecodeError:
                continue

    print(f"\n✅ 已将 {failed_count} 个失败运行标记为已完成")
    print(f"📁 输出文件: {output_file}")
    print(f"\n⚠️  注意: 这些运行的评分为 0，会影响统计结果")
    print(f"💡 建议: 备份原文件后，用 {output_file} 替换 {runs_file}")


def remove_failed_runs(runs_file: str = "results/runs.jsonl",
                       output_file: str = "results/runs_cleaned.jsonl"):
    """删除失败的运行记录"""
    runs_path = Path(runs_file)

    if not runs_path.exists():
        print(f"❌ 文件不存在: {runs_file}")
        return

    failed_count = 0
    kept_count = 0

    with open(runs_path, "r", encoding="utf-8") as f_in, \
         open(output_file, "w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
                if run.get("status") == "failed":
                    failed_count += 1
                else:
                    f_out.write(json.dumps(run, ensure_ascii=False) + "\n")
                    kept_count += 1
            except json.JSONDecodeError:
                continue

    print(f"\n✅ 已删除 {failed_count} 个失败运行")
    print(f"📁 保留 {kept_count} 个成功运行")
    print(f"📁 输出文件: {output_file}")
    print(f"\n💡 建议: 备份原文件后，用 {output_file} 替换 {runs_file}")


def main():
    parser = argparse.ArgumentParser(description="管理实验失败运行")
    parser.add_argument(
        "--runs-file",
        default="results/runs.jsonl",
        help="运行结果文件路径"
    )
    parser.add_argument(
        "--action",
        choices=["analyze", "mark-completed", "remove"],
        default="analyze",
        help="操作类型: analyze=分析失败, mark-completed=标记为已完成, remove=删除失败记录"
    )
    parser.add_argument(
        "--output",
        default="results/runs_cleaned.jsonl",
        help="输出文件路径（用于 mark-completed 和 remove）"
    )

    args = parser.parse_args()

    if args.action == "analyze":
        analyze_failed_runs(args.runs_file)
    elif args.action == "mark-completed":
        print("\n⚠️  警告: 此操作会将失败的运行标记为已完成（评分为 0）")
        confirm = input("确认继续? (yes/no): ")
        if confirm.lower() == "yes":
            mark_failed_as_completed(args.runs_file, args.output)
    elif args.action == "remove":
        print("\n⚠️  警告: 此操作会删除所有失败的运行记录")
        confirm = input("确认继续? (yes/no): ")
        if confirm.lower() == "yes":
            remove_failed_runs(args.runs_file, args.output)


if __name__ == "__main__":
    main()
