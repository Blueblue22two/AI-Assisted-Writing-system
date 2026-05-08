"""
Shared workspace for storing agent inputs, intermediate outputs, and results.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SharedWorkspace:
    """
    Central storage for all data during a single run.
    Agents read from and write to this workspace.
    """

    # Task definition
    task_id: str
    instruction: str
    source_material: str
    target_word_count: int
    rubric: Dict[str, int]

    # Agent outputs
    plan: Optional[str] = None
    draft: Optional[str] = None
    critique: Optional[str] = None
    final_answer: Optional[str] = None

    # Evaluation result
    evaluation: Optional[Dict[str, Any]] = None

    # Metadata
    condition: Optional[str] = None
    repetition_id: Optional[int] = None
    runtime_seconds: Optional[float] = None

    # Token accounting
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def add_tokens(self, input_tokens: int, output_tokens: int) -> None:
        """Accumulate token usage from an LLM call."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert workspace to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "condition": self.condition,
            "repetition_id": self.repetition_id,
            "instruction": self.instruction,
            "source_material": self.source_material,
            "target_word_count": self.target_word_count,
            "rubric": self.rubric,
            "plan": self.plan,
            "draft": self.draft,
            "critique": self.critique,
            "final_answer": self.final_answer,
            "evaluation": self.evaluation,
            "runtime_seconds": self.runtime_seconds,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
        }

    @classmethod
    def from_task_dict(cls, task: Dict[str, Any]) -> "SharedWorkspace":
        """Create a workspace from a task dictionary."""
        return cls(
            task_id=task["task_id"],
            instruction=task["instruction"],
            source_material=task.get("source_material", ""),
            target_word_count=task.get("target_word_count", 250),
            rubric=task.get("rubric", {}),
        )