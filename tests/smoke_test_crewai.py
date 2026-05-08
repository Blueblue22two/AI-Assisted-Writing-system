"""Minimal CrewAI connectivity smoke test for external LLM APIs."""

from __future__ import annotations

import argparse
import sys

from crewai import Agent, Crew, LLM, Process, Task

from src.config import load_config


def run_smoke_test(config_path: str, env_path: str) -> int:
    config, secrets = load_config(
        config_path=config_path,
        env_path=env_path,
        require_api_keys=True,
    )

    llm = LLM(
        model=config.llm.default_model,
        api_key=secrets.llm_api_key,
        base_url=config.llm.base_url,
        temperature=0.0,
    )

    agent = Agent(
        role="Connectivity Tester",
        goal="Return a fixed success token.",
        backstory="A minimal probe agent for connection checks.",
        llm=llm,
        verbose=False,
    )

    task = Task(
        description="Reply with exactly: CREWAI_CONNECTIVITY_OK",
        expected_output="CREWAI_CONNECTIVITY_OK",
        agent=agent,
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=False,
    )

    result = str(crew.kickoff()).strip()
    print(f"Smoke test result: {result}")
    if "CREWAI_CONNECTIVITY_OK" in result:
        print("Connectivity check passed.")
        return 0
    print("Connectivity check completed, but output token mismatch.")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--env", default=".env")
    args = parser.parse_args()

    try:
        return run_smoke_test(config_path=args.config, env_path=args.env)
    except Exception as exc:  # noqa: BLE001
        print(f"Connectivity check failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
