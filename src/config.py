"""
Configuration loader for the Multi-Agent Academic Writing Assistant.
Reads from config.yaml and environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """Central configuration manager for the entire system."""

    def __init__(self, config_path: str = "configs/config.yaml") -> None:
        """
        Initialize configuration by loading YAML and environment variables.

        Args:
            config_path: Path to the YAML configuration file.
        """
        load_dotenv()  # Load .env file
        self.config_path = Path(config_path)
        self._raw_config = self._load_yaml()
        self._validate()

    def _load_yaml(self) -> Dict[str, Any]:
        """Load and parse the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _validate(self) -> None:
        """Validate that required configuration sections exist."""
        required_sections = ["llm", "evaluator_llm", "experiment"]
        for section in required_sections:
            if section not in self._raw_config:
                raise ValueError(f"Missing required config section: {section}")

    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get configuration for generation LLM (Planner, Writer, Critic, Editor).

        Returns:
            Dictionary with provider, base_url, model, temperature, max_tokens.
        """
        cfg = self._raw_config["llm"]
        api_key = os.getenv(cfg.get("api_key_env", "LLM_API_KEY"))
        if not api_key:
            raise ValueError(f"Missing API key for LLM: {cfg.get('api_key_env')}")
        return {
            "provider": cfg.get("provider", "openai-compatible"),
            "base_url": cfg.get("base_url"),
            "api_key": api_key,
            "model": cfg.get("default_model", "gpt-4o-mini"),
            "temperature": cfg.get("temperature", 0.4),
            "max_tokens": cfg.get("max_tokens", 1200),
        }

    def get_evaluator_config(self) -> Dict[str, Any]:
        """
        Get configuration for Evaluator LLM.

        Returns:
            Dictionary with provider, base_url, model, temperature, max_tokens.
        """
        cfg = self._raw_config["evaluator_llm"]
        api_key = os.getenv(cfg.get("api_key_env", "EVALUATOR_API_KEY"))
        if not api_key:
            raise ValueError(f"Missing API key for Evaluator: {cfg.get('api_key_env')}")
        return {
            "provider": cfg.get("provider", "openai-compatible"),
            "base_url": cfg.get("base_url"),
            "api_key": api_key,
            "model": cfg.get("model", "gpt-4o"),
            "temperature": cfg.get("temperature", 0.0),
            "max_tokens": cfg.get("max_tokens", 1000),
        }

    def get_experiment_config(self) -> Dict[str, Any]:
        """Get experiment configuration (repetitions, output_dir, etc.)."""
        return self._raw_config["experiment"]

    @property
    def debug(self) -> bool:
        """Return True if debug mode is enabled."""
        return self._raw_config.get("debug", False)


# Singleton instance for global use
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """Get the singleton Config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance