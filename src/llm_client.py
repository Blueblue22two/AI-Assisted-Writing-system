"""Shared LLM client wrapper for non-CrewAI calls and evaluator support."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from openai import OpenAI

from src.config import EvaluatorLLMConfig, LLMConfig, RuntimeLLMSecrets

logger = logging.getLogger(__name__)


class LLMCallResult:
    """Result of an LLM API call with parsed response and metadata."""

    def __init__(
        self,
        content: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
        model: str = "",
        latency_ms: float = 0.0,
    ):
        self.content = content
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = total_tokens
        self.model = model
        self.latency_ms = latency_ms

    def __repr__(self) -> str:
        return (
            f"LLMCallResult(content={self.content[:50]}..., "
            f"tokens={self.total_tokens}, model={self.model})"
        )


class LLMClient:
    """Wrapper for OpenAI-compatible LLM API calls."""

    def __init__(
        self,
        config: LLMConfig | EvaluatorLLMConfig,
        api_key: str,
    ):
        self.config = config
        self.client = OpenAI(
            base_url=config.base_url,
            api_key=api_key,
        )

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> LLMCallResult:
        """
        Make a chat completion call to the LLM API.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Override configured temperature if provided.
            max_tokens: Override configured max_tokens if provided.
            model: Override configured model if provided.

        Returns:
            LLMCallResult with response content and token usage.
        """
        import time

        t_start = time.time()

        params: Dict[str, Any] = {
            "model": model or getattr(self.config, "default_model", "") or getattr(self.config, "model", ""),
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens,
        }

        try:
            response = self.client.chat.completions.create(**params)
        except Exception as exc:
            logger.error(f"LLM API call failed: {exc}")
            raise

        t_end = time.time()

        choice = response.choices[0]
        content = choice.message.content or ""

        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        return LLMCallResult(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            model=params["model"],
            latency_ms=(t_end - t_start) * 1000,
        )

    def structured_output(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        model: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Call LLM and parse the response as JSON.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Temperature for the call (default 0.0 for deterministic output).
            max_tokens: Override configured max_tokens if provided.
            model: Override configured model if provided.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            ValueError: If response cannot be parsed as JSON.
        """
        result = self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        )

        try:
            return json.loads(result.content)
        except json.JSONDecodeError as exc:
            logger.error(f"Failed to parse JSON response: {result.content[:200]}")
            raise ValueError(f"Invalid JSON response: {exc}") from exc


class LLMClientFactory:
    """Factory for creating LLM clients from configuration."""

    @staticmethod
    def create_generation_client(
        config: LLMConfig,
        secrets: RuntimeLLMSecrets,
    ) -> LLMClient:
        """Create an LLM client for generation agents."""
        return LLMClient(config, secrets.llm_api_key)

    @staticmethod
    def create_evaluator_client(
        config: EvaluatorLLMConfig,
        secrets: RuntimeLLMSecrets,
    ) -> LLMClient:
        """Create an LLM client for the evaluator agent."""
        return LLMClient(config, secrets.evaluator_api_key)