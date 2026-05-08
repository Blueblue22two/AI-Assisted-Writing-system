"""
Unified LLM client for API calls.
Supports OpenAI-compatible endpoints with retry logic.
"""

import json
import time
from typing import Any, Dict, List, Optional

import requests


class LLMClient:
    """Simple wrapper for OpenAI-compatible LLM API calls."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """
        Initialize the LLM client.

        Args:
            base_url: API endpoint URL.
            api_key: Authentication key.
            model: Model name to use.
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens: Maximum tokens in response.
            max_retries: Number of retries on failure.
            retry_delay: Delay in seconds between retries.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Send a chat completion request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'.

        Returns:
            Dictionary with 'content', 'input_tokens', 'output_tokens'.

        Raises:
            Exception: If all retries fail.
        """
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url, headers=self._get_headers(), json=payload, timeout=60
                )
                response.raise_for_status()
                data = response.json()

                # Extract response content
                content = data["choices"][0]["message"]["content"]

                # Extract token usage if available
                usage = data.get("usage", {})
                input_tokens = usage.get("prompt_tokens", 0)
                output_tokens = usage.get("completion_tokens", 0)

                return {
                    "content": content,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                }

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                continue

        raise Exception(f"LLM request failed after {self.max_retries} retries: {last_error}")

    def generate_with_system_prompt(
        self, system_prompt: str, user_prompt: str
    ) -> Dict[str, Any]:
        """
        Convenience method for single-turn chat with system prompt.

        Args:
            system_prompt: System message content.
            user_prompt: User message content.

        Returns:
            Same as generate().
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.generate(messages)