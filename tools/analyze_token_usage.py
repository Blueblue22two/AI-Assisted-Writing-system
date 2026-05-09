"""Aggregate token usage records by agent/model/condition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def load_token_usage(path: str) -> pd.DataFrame:
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"No token usage rows found in {path}")
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Analyze token usage logs")
    parser.add_argument("--input", default="results/token_usage.jsonl", help="Path to token usage jsonl")
    parser.add_argument("--output-dir", default="results", help="Directory for summary CSV outputs")
    args = parser.parse_args()

    df = load_token_usage(args.input)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = ["prompt_tokens", "completion_tokens", "total_tokens", "successful_requests"]

    by_agent = (
        df.groupby(["agent_name"])[metrics]
        .agg(["sum", "mean", "count"])
        .round(3)
    )
    by_model = (
        df.groupby(["model"])[metrics]
        .agg(["sum", "mean", "count"])
        .round(3)
    )
    by_condition = (
        df.groupby(["condition", "agent_name"])[metrics]
        .agg(["sum", "mean", "count"])
        .round(3)
    )

    by_agent.to_csv(out_dir / "token_summary_by_agent.csv", encoding="utf-8")
    by_model.to_csv(out_dir / "token_summary_by_model.csv", encoding="utf-8")
    by_condition.to_csv(out_dir / "token_summary_by_condition.csv", encoding="utf-8")

    print("Saved:")
    print(out_dir / "token_summary_by_agent.csv")
    print(out_dir / "token_summary_by_model.csv")
    print(out_dir / "token_summary_by_condition.csv")


if __name__ == "__main__":
    main()

