"""CLI entry point for aggregating and visualizing experiment results."""

import argparse
import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_runs(results_path: str) -> pd.DataFrame:
    """Load run results from JSONL file."""
    data = []
    with open(results_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                run = json.loads(line)
                row = {
                    "task_id": run["task_id"],
                    "condition": run["condition"],
                    "repetition_id": run["repetition_id"],
                    "run_id": run["run_id"],
                    "eval_id": run["eval_id"],
                    "overall_score": run["evaluation"]["overall_score"],
                    "runtime_seconds": run.get("runtime_seconds", 0.0),
                }
                for metric, score in run["evaluation"]["scores"].items():
                    row[metric] = score
                data.append(row)
            except (json.JSONDecodeError, KeyError) as exc:
                logging.warning(f"Skipping malformed run: {exc}")

    if not data:
        raise ValueError("No valid runs found in results file")

    return pd.DataFrame(data)


def aggregate_by_condition(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate scores by condition."""
    metrics = ["overall_score", "relevance", "structure", "evidence_use", "argument_clarity", "academic_style", "grammar_readability"]
    
    agg_df = df.groupby(["condition", "task_id"])[metrics].mean().reset_index()
    
    condition_stats = agg_df.groupby("condition")[metrics].agg([
        "mean", "std", "min", "max"
    ]).round(3)
    
    return condition_stats


def aggregate_by_task_condition(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate scores by task and condition."""
    metrics = ["overall_score", "relevance", "structure", "evidence_use", "argument_clarity", "academic_style", "grammar_readability"]
    
    return df.groupby(["task_id", "condition"])[metrics].mean().reset_index()


def generate_mean_scores_chart(df: pd.DataFrame, output_dir: str):
    """Generate bar chart showing mean scores by condition."""
    agg_df = df.groupby("condition")["overall_score"].agg(["mean", "std"]).reset_index()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=agg_df, x="condition", y="mean")
    
    plt.title("Mean Overall Score by Experimental Condition")
    plt.xlabel("Condition")
    plt.ylabel("Mean Overall Score (1-5)")
    plt.ylim(0, 5.5)
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(Path(output_dir, "mean_scores.png"), dpi=300, bbox_inches="tight")
    plt.close()


def generate_score_distribution_chart(df: pd.DataFrame, output_dir: str):
    """Generate histogram showing score distribution by condition."""
    plt.figure(figsize=(12, 6))
    
    sns.histplot(
        data=df,
        x="overall_score",
        hue="condition",
        kde=True,
        bins=20,
        alpha=0.6,
        stat="density"
    )
    
    plt.title("Distribution of Overall Scores by Condition")
    plt.xlabel("Overall Score")
    plt.ylabel("Density")
    plt.xlim(1, 5)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(Path(output_dir, "score_distribution.png"), dpi=300, bbox_inches="tight")
    plt.close()


def generate_detailed_metrics_chart(df: pd.DataFrame, output_dir: str):
    """Generate grouped bar chart for all metrics by condition."""
    metrics = ["relevance", "structure", "evidence_use", "argument_clarity", "academic_style", "grammar_readability"]
    metric_labels = ["Relevance", "Structure", "Evidence Use", "Argument Clarity", "Academic Style", "Grammar"]
    
    agg_df = df.groupby("condition")[metrics].mean().reset_index()
    
    plt.figure(figsize=(14, 7))
    
    bar_width = 0.25
    conditions = agg_df["condition"].unique()
    x = range(len(metrics))
    
    for i, condition in enumerate(conditions):
        means = agg_df[agg_df["condition"] == condition][metrics].values.flatten()
        plt.bar([xi + i * bar_width for xi in x], means, width=bar_width, label=condition)
    
    plt.title("Mean Scores by Metric and Condition")
    plt.xlabel("Metric")
    plt.ylabel("Mean Score (1-5)")
    plt.xticks([xi + bar_width for xi in x], metric_labels, rotation=30)
    plt.ylim(0, 5.5)
    plt.legend(title="Condition")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(Path(output_dir, "detailed_metrics.png"), dpi=300, bbox_inches="tight")
    plt.close()


def generate_runtime_chart(df: pd.DataFrame, output_dir: str):
    """Generate bar chart showing mean runtime by condition."""
    agg_df = df.groupby("condition")["runtime_seconds"].agg(["mean", "std"]).reset_index()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=agg_df, x="condition", y="mean")
    
    plt.title("Mean Runtime by Experimental Condition")
    plt.xlabel("Condition")
    plt.ylabel("Runtime (seconds)")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(Path(output_dir, "runtime.png"), dpi=300, bbox_inches="tight")
    plt.close()


def compute_win_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Compute win rates between conditions (paired comparison)."""
    conditions = df["condition"].unique()
    results = []
    
    for i, cond1 in enumerate(conditions):
        for j, cond2 in enumerate(conditions):
            if i >= j:
                continue
            
            # Group by task_id and condition, take mean of repetitions
            subset = df[df["condition"].isin([cond1, cond2])]
            grouped = subset.groupby(["task_id", "condition"])["overall_score"].mean().reset_index()
            
            paired = grouped.pivot(
                index="task_id",
                columns="condition",
                values="overall_score"
            ).dropna()
            
            wins = (paired[cond1] > paired[cond2]).sum()
            ties = (paired[cond1] == paired[cond2]).sum()
            losses = (paired[cond1] < paired[cond2]).sum()
            total = len(paired)
            
            results.append({
                "condition_1": cond1,
                "condition_2": cond2,
                "wins": wins,
                "ties": ties,
                "losses": losses,
                "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
                "mean_diff": round((paired[cond1] - paired[cond2]).mean(), 3),
            })
    
    return pd.DataFrame(results)


def save_scores_csv(df: pd.DataFrame, output_dir: str):
    """Save flattened scores to CSV."""
    df.to_csv(Path(output_dir, "scores.csv"), index=False, encoding="utf-8")


def save_summary_csv(condition_stats: pd.DataFrame, win_rates: pd.DataFrame, output_dir: str):
    """Save summary statistics to CSV."""
    condition_stats.to_csv(Path(output_dir, "condition_summary.csv"), encoding="utf-8")
    win_rates.to_csv(Path(output_dir, "win_rates.csv"), index=False, encoding="utf-8")


def print_summary(condition_stats: pd.DataFrame, win_rates: pd.DataFrame):
    """Print summary statistics to console."""
    print("\n=== Condition Summary Statistics ===")
    print(condition_stats)
    
    print("\n=== Win Rates (Paired Comparisons) ===")
    print(win_rates)


def main():
    """Main entry point for analyzing experiment results."""
    parser = argparse.ArgumentParser(description="Analyze and visualize experiment results")
    parser.add_argument(
        "--results",
        default="results/runs.jsonl",
        help="Path to runs JSONL file"
    )
    parser.add_argument(
        "--output-dir",
        default="results",
        help="Output directory for charts and CSV files"
    )
    
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(__name__)

    try:
        logger.info("Loading run results")
        df = load_runs(args.results)
        
        logger.info("Generating summary statistics")
        condition_stats = aggregate_by_condition(df)
        win_rates = compute_win_rates(df)
        
        logger.info("Saving CSV files")
        save_scores_csv(df, args.output_dir)
        save_summary_csv(condition_stats, win_rates, args.output_dir)
        
        logger.info("Generating charts")
        generate_mean_scores_chart(df, args.output_dir)
        generate_score_distribution_chart(df, args.output_dir)
        generate_detailed_metrics_chart(df, args.output_dir)
        generate_runtime_chart(df, args.output_dir)
        
        print_summary(condition_stats, win_rates)
        
        logger.info("Analysis completed successfully")

    except Exception as exc:
        logger.error(f"Analysis failed: {exc}", exc_info=True)
        raise


if __name__ == "__main__":
    main()