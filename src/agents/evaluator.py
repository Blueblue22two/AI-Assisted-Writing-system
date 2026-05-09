"""Evaluator Agent prompt and configuration."""

from typing import Any, Dict

from src.config import PRIMARY_METRICS, WritingRubric
from src.environment import EvaluationResult
from src.llm_client import LLMClient


class EvaluatorAgent:
    """Evaluator Agent for scoring academic writing based on rubric."""

    RUBRIC_DESCRIPTIONS = {
        "relevance": """Evaluates whether the answer directly addresses the writing task and remains focused on the instruction.
- 1: The answer is largely irrelevant or fails to address the task.
- 2: The answer only partially addresses the task and misses major requirements.
- 3: The answer addresses the task in a basic way but may be incomplete or generic.
- 4: The answer is relevant and covers most task requirements clearly.
- 5: The answer fully addresses the task with strong focus and no major omissions.""",
        "structure": """Evaluates the organization of ideas, paragraph structure, logical flow, and coherence.
- 1: The answer is disorganized and difficult to follow.
- 2: The answer has weak organization with unclear connections between ideas.
- 3: The answer has a basic structure, but the flow or transitions are limited.
- 4: The answer is well organized with mostly clear logical progression.
- 5: The answer is highly coherent, well structured, and logically developed.""",
        "evidence_use": """Evaluates how effectively the answer uses the source material or background information to support claims.
- 1: The answer does not use the source material or uses it inaccurately.
- 2: The answer makes minimal or vague use of the source material.
- 3: The answer uses some relevant evidence, but support is limited or underdeveloped.
- 4: The answer uses relevant evidence appropriately to support most claims.
- 5: The answer uses source material accurately, specifically, and effectively throughout.""",
        "argument_clarity": """Evaluates whether the central argument is clear, well reasoned, and critically developed.
- 1: The answer lacks a clear argument or contains flawed reasoning.
- 2: The argument is weak, unclear, or insufficiently developed.
- 3: The answer presents a basic argument, but reasoning may be shallow or uneven.
- 4: The argument is clear, reasonable, and mostly well developed.
- 5: The argument is precise, persuasive, and shows strong critical reasoning.""",
        "academic_style": """Evaluates whether the language is appropriate for academic writing.
- 1: The language is informal, inappropriate, or unsuitable for academic writing.
- 2: The language is sometimes informal, vague, or imprecise.
- 3: The style is generally academic but may contain repetitive or generic phrasing.
- 4: The language is clear, formal, and mostly precise.
- 5: The language is consistently formal, precise, objective, and academically appropriate.""",
        "grammar_readability": """Evaluates grammatical accuracy, fluency, and ease of reading.
- 1: Frequent grammar or readability problems seriously affect understanding.
- 2: Several language issues make parts of the answer difficult to read.
- 3: The answer is generally understandable but contains noticeable language issues.
- 4: The answer is fluent and readable with only minor language issues.
- 5: The answer is fluent, clear, grammatically accurate, and easy to read.""",
    }

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_prompt(self, eval_id: str, instruction: str, source_material: str, target_word_count: int, rubric: WritingRubric, answer: str) -> str:
        """Generate prompt for Evaluator Agent."""
        rubric_desc = "\n".join([f"## {metric.replace('_', ' ').title()}\n{self.RUBRIC_DESCRIPTIONS[metric]}" for metric in PRIMARY_METRICS])

        return f"""
You are an independent academic writing evaluator.

Evaluate the answer according to the given writing task, source material, target word count, and rubric.

You must not assume anything about how the answer was generated.
You must not reward or penalize the answer based on any workflow.
Evaluate only the quality of the final answer.

Use a 1-5 integer scale for each dimension:
1 = very poor
2 = weak
3 = acceptable
4 = good
5 = excellent

Return only valid JSON with the following fields:
- eval_id: string (the evaluation ID)
- scores: object with keys: relevance, structure, evidence_use, argument_clarity, academic_style, grammar_readability
- overall_score: number (average of all dimension scores)
- justification: string (brief explanation, max 80 words)

Writing task:
{instruction}

Source material:
{source_material}

Target word count:
{target_word_count}

Rubric dimensions with scoring guidelines:
{rubric_desc}

Answer:
{answer}
"""

    def evaluate(self, eval_id: str, instruction: str, source_material: str, target_word_count: int, rubric: WritingRubric, answer: str) -> EvaluationResult:
        """
        Evaluate an answer and return structured evaluation result.

        Args:
            eval_id: Unique identifier for this evaluation
            instruction: The writing task instruction
            source_material: The source material provided
            target_word_count: Target word count for the task
            rubric: The evaluation rubric
            answer: The answer to evaluate

        Returns:
            EvaluationResult with scores and justification
        """
        prompt = self.generate_prompt(eval_id, instruction, source_material, target_word_count, rubric, answer)

        messages = [{"role": "system", "content": "You are an impartial academic writing evaluator."}, {"role": "user", "content": prompt}]

        try:
            result = self.llm_client.structured_output(messages, temperature=0.0)
        except ValueError:
            return self._repair_and_retry(eval_id, instruction, source_material, target_word_count, rubric, answer, prompt)

        return self._parse_result(result, eval_id)

    def _repair_and_retry(self, eval_id: str, instruction: str, source_material: str, target_word_count: int, rubric: WritingRubric, answer: str, original_prompt: str) -> EvaluationResult:
        """Attempt to repair a failed JSON parse by requesting a fix."""
        repair_prompt = f"""
Your previous response was not valid JSON. Please fix it and return ONLY valid JSON with no additional text.

Original prompt:
{original_prompt}

Please return valid JSON with: eval_id, scores (object with relevance, structure, evidence_use, argument_clarity, academic_style, grammar_readability), overall_score, justification
"""
        messages = [{"role": "user", "content": repair_prompt}]
        try:
            result = self.llm_client.structured_output(messages, temperature=0.0)
            return self._parse_result(result, eval_id)
        except ValueError:
            return EvaluationResult(
                eval_id=eval_id,
                scores={metric: 1 for metric in PRIMARY_METRICS},
                overall_score=1.0,
                justification="Failed to parse evaluator response",
            )

    def _parse_result(self, result: Dict[str, Any], eval_id: str) -> EvaluationResult:
        """Parse LLM response into EvaluationResult."""
        scores = result.get("scores", {})

        for metric in PRIMARY_METRICS:
            if metric not in scores:
                scores[metric] = 1
            else:
                scores[metric] = int(scores[metric])

        overall_score = result.get("overall_score")
        if overall_score is None:
            valid_scores = [s for s in scores.values() if 1 <= s <= 5]
            overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 1.0
        else:
            overall_score = float(overall_score)

        justification = result.get("justification", "").strip()[:80]

        return EvaluationResult(
            eval_id=eval_id,
            scores=scores,
            overall_score=overall_score,
            justification=justification,
        )