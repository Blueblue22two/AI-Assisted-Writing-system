"""Configuration loading, task schema validation, and JSONL task loading."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


PRIMARY_METRICS = (
    "relevance",
    "structure",
    "evidence_use",
    "argument_clarity",
    "academic_style",
    "grammar_readability",
)


class ConfigurationError(ValueError):
    """Raised when config structure or environment binding is invalid."""


class MissingAPIKeyError(ConfigurationError):
    """Raised when the configured API key environment variable is missing."""


class TaskLoadError(ValueError):
    """Raised when task JSONL parsing or schema validation fails."""


class LLMConfig(BaseModel):
    """Non-secret model configuration used by generation agents."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    base_url: str
    api_key_env: str
    default_model: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(gt=0)
    api_call_delay: float = Field(default=0.0, ge=0.0, description="Delay in seconds after each API call")


class EvaluatorLLMConfig(BaseModel):
    """Non-secret model configuration used by evaluator agent."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    base_url: str
    api_key_env: str
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: int = Field(gt=0)
    api_call_delay: float = Field(default=0.0, ge=0.0, description="Delay in seconds after each API call")


class ExperimentConfig(BaseModel):
    """Experiment runtime configuration."""

    model_config = ConfigDict(extra="forbid")

    repetitions: int = Field(gt=0)
    output_dir: str = Field(min_length=1)


class AppConfig(BaseModel):
    """Top-level app configuration loaded from YAML."""

    model_config = ConfigDict(extra="forbid")

    llm: LLMConfig
    evaluator_llm: EvaluatorLLMConfig
    experiment: ExperimentConfig


class RuntimeLLMSecrets(BaseModel):
    """Resolved environment secrets for runtime calls."""

    model_config = ConfigDict(extra="forbid")

    llm_api_key: str = Field(repr=False, min_length=1)
    evaluator_api_key: str = Field(repr=False, min_length=1)


class WritingRubric(BaseModel):
    """Rubric schema constrained to six primary metrics."""

    model_config = ConfigDict(extra="forbid")

    relevance: int = Field(ge=1, le=5)
    structure: int = Field(ge=1, le=5)
    evidence_use: int = Field(ge=1, le=5)
    argument_clarity: int = Field(ge=1, le=5)
    academic_style: int = Field(ge=1, le=5)
    grammar_readability: int = Field(ge=1, le=5)

    @model_validator(mode="before")
    @classmethod
    def check_required_metrics(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            raise ValueError("rubric must be a JSON object")
        keys = set(value.keys())
        expected = set(PRIMARY_METRICS)
        missing = expected - keys
        extra = keys - expected
        if missing or extra:
            details = []
            if missing:
                details.append(f"missing={sorted(missing)}")
            if extra:
                details.append(f"unexpected={sorted(extra)}")
            raise ValueError(
                "rubric must contain exactly six primary metrics: "
                + ", ".join(PRIMARY_METRICS)
                + f" ({'; '.join(details)})"
            )
        return value


class WritingTask(BaseModel):
    """Writing task schema loaded from JSONL dataset files."""

    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    source_material: str = Field(min_length=1)
    target_word_count: int = Field(gt=0)
    rubric: WritingRubric

    @field_validator("task_id", "instruction", "source_material")
    @classmethod
    def not_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("must not be blank")
        return stripped


def load_app_config(config_path: str | Path = "configs/config.yaml") -> AppConfig:
    """Load and validate non-secret YAML configuration."""

    path = Path(config_path)
    if not path.exists():
        raise ConfigurationError(f"Config file not found: {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML format in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigurationError(f"Config root must be a mapping object: {path}")

    try:
        return AppConfig.model_validate(data)
    except ValidationError as exc:
        raise ConfigurationError(f"Invalid config schema in {path}: {exc}") from exc


def resolve_runtime_secrets(
    config: AppConfig,
    env_path: str | Path = ".env",
    require_keys: bool = True,
) -> RuntimeLLMSecrets:
    """
    Resolve API keys from environment variables defined in config.

    Keys are never logged and are hidden in object repr.
    """

    load_dotenv(dotenv_path=Path(env_path), override=False)

    llm_api_key = os.getenv(config.llm.api_key_env, "").strip()
    evaluator_api_key = os.getenv(config.evaluator_llm.api_key_env, "").strip()

    if require_keys:
        if not llm_api_key:
            raise MissingAPIKeyError(
                f"Missing API key environment variable: {config.llm.api_key_env}"
            )
        if not evaluator_api_key:
            raise MissingAPIKeyError(
                f"Missing API key environment variable: {config.evaluator_llm.api_key_env}"
            )

    return RuntimeLLMSecrets(
        llm_api_key=llm_api_key,
        evaluator_api_key=evaluator_api_key,
    )


def load_config(
    config_path: str | Path = "configs/config.yaml",
    env_path: str | Path = ".env",
    require_api_keys: bool = True,
) -> tuple[AppConfig, RuntimeLLMSecrets]:
    """Load validated app config plus resolved runtime secrets."""

    config = load_app_config(config_path)
    secrets = resolve_runtime_secrets(
        config=config,
        env_path=env_path,
        require_keys=require_api_keys,
    )
    return config, secrets


def load_tasks_jsonl(tasks_path: str | Path) -> list[WritingTask]:
    """Load and validate writing tasks from JSONL file."""

    path = Path(tasks_path)
    if not path.exists():
        raise TaskLoadError(f"Task file not found: {path}")

    tasks: list[WritingTask] = []
    seen_task_ids: set[str] = set()

    with path.open("r", encoding="utf-8") as f:
        for line_number, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TaskLoadError(
                    f"Invalid JSON in {path} at line {line_number}: {exc.msg}"
                ) from exc

            try:
                task = WritingTask.model_validate(payload)
            except ValidationError as exc:
                raise TaskLoadError(
                    f"Invalid task schema in {path} at line {line_number}: {exc}"
                ) from exc

            if task.task_id in seen_task_ids:
                raise TaskLoadError(
                    f"Duplicate task_id '{task.task_id}' in {path} at line {line_number}"
                )
            seen_task_ids.add(task.task_id)
            tasks.append(task)

    if not tasks:
        raise TaskLoadError(f"No valid tasks found in {path}")

    return tasks
