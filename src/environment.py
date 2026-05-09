"""Language-based academic writing environment and shared workspace models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.config import WritingRubric, WritingTask


@dataclass
class WritingPlan:
    """Output structure for Planner Agent."""

    thesis_statement: str
    paragraph_outline: list[str]
    key_arguments: list[str]
    evidence_plan: Dict[str, str]


@dataclass
class CritiqueResult:
    """Output structure for Critic Agent."""

    strengths: list[str]
    weaknesses: list[str]
    revision_suggestions: list[str]


@dataclass
class EvaluationResult:
    """Output structure for Evaluator Agent."""

    eval_id: str
    scores: Dict[str, int]
    overall_score: float
    justification: str


@dataclass
class GenerationTrace:
    """Complete trace of a single generation run."""

    plan: Optional[str] = None
    draft: Optional[str] = None
    critique: Optional[str] = None
    revised_draft: Optional[str] = None
    final_answer: Optional[str] = None


@dataclass
class RunMetadata:
    """Metadata for a single experiment run."""

    task_id: str
    condition: str
    repetition_id: int
    runtime_seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    model_info: str = ""


@dataclass
class SharedWorkspace:
    """Shared workspace for agent communication and state tracking."""

    task: Optional[WritingTask] = None
    plan: Optional[str] = None
    draft: Optional[str] = None
    critique: Optional[str] = None
    final_answer: Optional[str] = None
    evaluation_result: Optional[EvaluationResult] = None
    generation_trace: GenerationTrace = None
    run_metadata: RunMetadata = None

    def __post_init__(self):
        if self.generation_trace is None:
            self.generation_trace = GenerationTrace()
        if self.run_metadata is None:
            self.run_metadata = RunMetadata(task_id="", condition="", repetition_id=0)

    def update_plan(self, plan: str) -> None:
        """Update the writing plan."""
        self.plan = plan
        self.generation_trace.plan = plan

    def update_draft(self, draft: str) -> None:
        """Update the draft."""
        self.draft = draft
        self.generation_trace.draft = draft

    def update_critique(self, critique: str) -> None:
        """Update the critique."""
        self.critique = critique
        self.generation_trace.critique = critique

    def update_final_answer(self, final_answer: str) -> None:
        """Update the final answer."""
        self.final_answer = final_answer
        self.generation_trace.final_answer = final_answer

    def update_evaluation(self, evaluation: EvaluationResult) -> None:
        """Update the evaluation result."""
        self.evaluation_result = evaluation

    def reset(self, task: WritingTask, condition: str, repetition_id: int) -> None:
        """Reset workspace for a new task run."""
        self.task = task
        self.plan = None
        self.draft = None
        self.critique = None
        self.final_answer = None
        self.evaluation_result = None
        self.generation_trace = GenerationTrace()
        self.run_metadata = RunMetadata(
            task_id=task.task_id,
            condition=condition,
            repetition_id=repetition_id,
        )

    def to_json(self) -> str:
        """Serialize workspace state to JSON."""
        data = {
            "task": self.task.model_dump() if self.task else None,
            "plan": self.plan,
            "draft": self.draft,
            "critique": self.critique,
            "final_answer": self.final_answer,
            "evaluation_result": {
                "eval_id": self.evaluation_result.eval_id,
                "scores": self.evaluation_result.scores,
                "overall_score": self.evaluation_result.overall_score,
                "justification": self.evaluation_result.justification,
            } if self.evaluation_result else None,
            "run_metadata": {
                "task_id": self.run_metadata.task_id,
                "condition": self.run_metadata.condition,
                "repetition_id": self.run_metadata.repetition_id,
                "runtime_seconds": self.run_metadata.runtime_seconds,
                "input_tokens": self.run_metadata.input_tokens,
                "output_tokens": self.run_metadata.output_tokens,
                "total_tokens": self.run_metadata.total_tokens,
                "estimated_cost": self.run_metadata.estimated_cost,
                "model_info": self.run_metadata.model_info,
            },
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


class WritingEnvironment:
    """Language-based academic writing environment."""

    def __init__(self):
        self.workspace = SharedWorkspace()

    def setup_task(self, task: WritingTask, condition: str, repetition_id: int) -> None:
        """Initialize environment with a new writing task."""
        self.workspace.reset(task, condition, repetition_id)

    def execute_action(self, action: str, **kwargs) -> None:
        """Execute an agent action and update workspace state."""
        if action == "plan":
            self.workspace.update_plan(kwargs.get("plan", ""))
        elif action == "write":
            self.workspace.update_draft(kwargs.get("draft", ""))
        elif action == "critique":
            self.workspace.update_critique(kwargs.get("critique", ""))
        elif action == "revise":
            self.workspace.update_final_answer(kwargs.get("final_answer", ""))
        elif action == "evaluate":
            self.workspace.update_evaluation(kwargs.get("evaluation", None))
        else:
            raise ValueError(f"Unknown action: {action}")

    def get_state(self) -> dict[str, Any]:
        """Get current environment state."""
        return {
            "task_id": self.workspace.run_metadata.task_id,
            "condition": self.workspace.run_metadata.condition,
            "has_plan": self.workspace.plan is not None,
            "has_draft": self.workspace.draft is not None,
            "has_critique": self.workspace.critique is not None,
            "has_final_answer": self.workspace.final_answer is not None,
            "has_evaluation": self.workspace.evaluation_result is not None,
        }

    def is_complete(self) -> bool:
        """Check if the writing task is complete (has final answer and evaluation)."""
        return (
            self.workspace.final_answer is not None
            and self.workspace.evaluation_result is not None
        )