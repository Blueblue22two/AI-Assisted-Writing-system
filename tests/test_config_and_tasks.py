from __future__ import annotations

from pathlib import Path

import pytest

from src.config import (
    ConfigurationError,
    MissingAPIKeyError,
    TaskLoadError,
    load_app_config,
    load_config,
    load_tasks_jsonl,
    resolve_runtime_secrets,
)


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_load_app_config_success() -> None:
    config = load_app_config("configs/config.yaml")
    assert config.llm.default_model == "deepseek-v4-flash"
    assert config.evaluator_llm.model == "gpt-5.2"
    assert config.experiment.repetitions > 0


def test_load_app_config_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.yaml"
    with pytest.raises(ConfigurationError, match="Config file not found"):
        load_app_config(missing_path)


def test_load_app_config_invalid_schema(tmp_path: Path) -> None:
    invalid_config = tmp_path / "config.yaml"
    write_file(
        invalid_config,
        """
llm:
  provider: "openai-compatible"
""".strip(),
    )
    with pytest.raises(ConfigurationError, match="Invalid config schema"):
        load_app_config(invalid_config)


def test_resolve_runtime_secrets_success(monkeypatch: pytest.MonkeyPatch) -> None:
    config = load_app_config("configs/config.yaml")
    monkeypatch.setenv(config.llm.api_key_env, "test-llm-key")
    monkeypatch.setenv(config.evaluator_llm.api_key_env, "test-eval-key")

    secrets = resolve_runtime_secrets(config, require_keys=True)
    assert secrets.llm_api_key == "test-llm-key"
    assert secrets.evaluator_api_key == "test-eval-key"
    assert "test-llm-key" not in repr(secrets)
    assert "test-eval-key" not in repr(secrets)


def test_resolve_runtime_secrets_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    config = load_app_config("configs/config.yaml")
    monkeypatch.delenv(config.llm.api_key_env, raising=False)
    monkeypatch.delenv(config.evaluator_llm.api_key_env, raising=False)
    missing_env = tmp_path / "missing.env"

    with pytest.raises(MissingAPIKeyError, match="Missing API key environment variable"):
        resolve_runtime_secrets(config, env_path=missing_env, require_keys=True)


def test_load_config_combined(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setenv("EVALUATOR_API_KEY", "y")
    config, secrets = load_config(require_api_keys=True)
    assert config.llm.api_key_env == "LLM_API_KEY"
    assert secrets.llm_api_key == "x"


def test_load_tasks_jsonl_success_debug_and_main() -> None:
    debug_tasks = load_tasks_jsonl("data/tasks_debug.jsonl")
    main_tasks = load_tasks_jsonl("data/tasks_main.jsonl")
    assert len(debug_tasks) >= 1
    assert len(main_tasks) >= 1
    assert all(task.rubric.argument_clarity == 5 for task in debug_tasks)


def test_load_tasks_jsonl_invalid_json(tmp_path: Path) -> None:
    task_file = tmp_path / "tasks.jsonl"
    write_file(task_file, '{"task_id":"T001"\n')
    with pytest.raises(TaskLoadError, match="Invalid JSON"):
        load_tasks_jsonl(task_file)


def test_load_tasks_jsonl_missing_required_fields(tmp_path: Path) -> None:
    task_file = tmp_path / "tasks.jsonl"
    write_file(
        task_file,
        (
            '{"task_id":"T001","instruction":"x","target_word_count":250,'
            '"rubric":{"relevance":5,"structure":5,"evidence_use":5,'
            '"argument_clarity":5,"academic_style":5,"grammar_readability":5}}'
        ),
    )
    with pytest.raises(TaskLoadError, match="Invalid task schema"):
        load_tasks_jsonl(task_file)


def test_load_tasks_jsonl_invalid_rubric_metrics(tmp_path: Path) -> None:
    task_file = tmp_path / "tasks.jsonl"
    write_file(
        task_file,
        (
            '{"task_id":"T001","instruction":"x","source_material":"y","target_word_count":250,'
            '"rubric":{"relevance":5,"structure":5,"evidence_use":5,"clarity":5,'
            '"academic_style":5,"grammar_readability":5}}'
        ),
    )
    with pytest.raises(TaskLoadError, match="primary metrics"):
        load_tasks_jsonl(task_file)


def test_load_tasks_jsonl_duplicate_task_id(tmp_path: Path) -> None:
    task_file = tmp_path / "tasks.jsonl"
    line = (
        '{"task_id":"T001","instruction":"x","source_material":"y","target_word_count":250,'
        '"rubric":{"relevance":5,"structure":5,"evidence_use":5,"argument_clarity":5,'
        '"academic_style":5,"grammar_readability":5}}'
    )
    write_file(task_file, f"{line}\n{line}\n")
    with pytest.raises(TaskLoadError, match="Duplicate task_id"):
        load_tasks_jsonl(task_file)
