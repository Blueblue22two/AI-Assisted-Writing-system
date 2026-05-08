"""Smoke test both configured models with a simple 'hello' prompt."""

from __future__ import annotations

import argparse
import sys

from openai import OpenAI

from src.config import load_config


def call_model(base_url: str, api_key: str, model: str, message: str) -> str:
    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": message}],
        temperature=0.0,
        max_tokens=128,
    )
    content = response.choices[0].message.content or ""
    return content.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/config.yaml")
    parser.add_argument("--env", default=".env")
    args = parser.parse_args()

    config, secrets = load_config(
        config_path=args.config,
        env_path=args.env,
        require_api_keys=True,
    )

    ok = True

    try:
        llm_reply = call_model(
            base_url=config.llm.base_url,
            api_key=secrets.llm_api_key,
            model=config.llm.default_model,
            message="hello",
        )
        print(f"[generation:{config.llm.default_model}] {llm_reply}")
        if not llm_reply:
            print("Generation model returned empty content.", file=sys.stderr)
            ok = False
    except Exception as exc:  # noqa: BLE001
        print(f"[generation:{config.llm.default_model}] FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        ok = False

    try:
        evaluator_reply = call_model(
            base_url=config.evaluator_llm.base_url,
            api_key=secrets.evaluator_api_key,
            model=config.evaluator_llm.model,
            message="hello",
        )
        print(f"[evaluator:{config.evaluator_llm.model}] {evaluator_reply}")
        if not evaluator_reply:
            print("Evaluator model returned empty content.", file=sys.stderr)
            ok = False
    except Exception as exc:  # noqa: BLE001
        print(f"[evaluator:{config.evaluator_llm.model}] FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        ok = False

    if ok:
        print("Two-model hello smoke test passed.")
        return 0
    print("Two-model hello smoke test failed.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
