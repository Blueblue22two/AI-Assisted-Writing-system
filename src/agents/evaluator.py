"""Evaluator Agent prompt and configuration."""

from typing import Any, Dict

from src.config import PRIMARY_METRICS, WritingRubric
from src.environment import EvaluationResult
from src.llm_client import LLMClient


class EvaluatorAgent:
    """Evaluator Agent for scoring academic writing based on rubric."""

    RUBRIC_DESCRIPTIONS = {
        "relevance": """Extremely strict. 5=perfectly addresses every nuance of the task with zero omission or digression (almost never give 5). 4=addresses all requirements but lacks depth or precision in at least one area. 3=misses at least one major requirement or has noticeable digression. 2=only addresses minor aspects; major omissions. 1=largely irrelevant or off-task.""",

        "structure": """Extremely strict. 5=flawless organization, every paragraph has perfect purpose and transition (almost never give 5). 4=well organized with clear flow but minor structural issue exists. 3=basic structure but inconsistent flow or weak transitions. 2=weak organization; paragraphs lack clear purpose. 1=disorganized and difficult to follow.""",

        "evidence_use": """Extremely strict. 5=every claim anchored to explicit source evidence with seamless integration (almost never give 5). 4=most claims supported with relevant evidence but one claim weak or integration could be tighter. 3=some evidence present but support limited or underdeveloped. 2=minimal or vague use; claims mostly unsupported. 1=no use or inaccurate use of source.""",

        "argument_clarity": """Extremely strict. 5=nuanced, persuasive, critically sophisticated argument with addressed counterpoints (almost never give 5). 4=clear, reasonable argument but lacks full nuance or sophistication. 3=basic argument but shallow, predictable, or lacking critical depth. 2=weak or unclear argument; reader must infer main point. 1=no discernible argument or fundamentally flawed reasoning.""",

        "academic_style": """Extremely strict. 5=consistently formal, precise, elegant academic register (almost never give 5). 4=formal and clear but occasional phrasing could be more precise or sophisticated. 3=generally academic but has repetitive, generic, or awkward phrasing. 2=noticeably informal, vague, or imprecise at times. 1=completely inappropriate for academic writing.""",

        "grammar_readability": """Extremely strict. 5=perfectly fluent, grammatically flawless, sophisticated sentence structures (almost never give 5). 4=fluent with only minor, occasional issues that don't impede understanding. 3=generally understandable but has noticeable errors. 2=several issues making parts hard to read. 1=frequent errors seriously affecting understanding.""",
    }

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def generate_prompt(self, eval_id: str, instruction: str, source_material: str, target_word_count: int, rubric: WritingRubric, answer: str) -> str:
        """Generate prompt for Evaluator Agent."""
        rubric_desc = "\n".join([f"## {metric.replace('_', ' ').title()}\n{self.RUBRIC_DESCRIPTIONS[metric]}" for metric in PRIMARY_METRICS])

        return f"""
You are an extremely strict, independent academic writing evaluator.

Evaluate the answer according to the given writing task, source material, target word count, and rubric.

You must not assume anything about how the answer was generated.
You must not reward or penalize the answer based on any workflow.
Evaluate only the quality of the final answer.

Use a 1-5 scale for each dimension (supports decimal values like 4.5, 3.7, 4.2, etc.):
1 = very poor
2 = weak
3 = acceptable
4 = good
5 = excellent (almost never give 5 - reserve for truly flawless work)

BE HARSH. A score of 4 means "good but noticeably imperfect". Most competent answers should score between 2.5 and 4.0.

Return only valid JSON with the following fields:
- eval_id: string (the evaluation ID)
- scores: object with keys: relevance, structure, evidence_use, argument_clarity, academic_style, grammar_readability (values should be numbers, can be decimals like 3.5)
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

        messages = [{"role": "system", "content": "You are an extremely strict, impartial academic writing evaluator. Be harsh. Do not give 5 unless the work is truly flawless."}, {"role": "user", "content": prompt}]

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
                scores={metric: 1.0 for metric in PRIMARY_METRICS},
                overall_score=1.0,
                justification="Failed to parse evaluator response",
            )

    def _parse_result(self, result: Dict[str, Any], eval_id: str) -> EvaluationResult:
        """Parse LLM response into EvaluationResult."""
        scores = result.get("scores", {})

        for metric in PRIMARY_METRICS:
            if metric not in scores:
                scores[metric] = 1.0
            else:
                val = scores[metric]
                if isinstance(val, (int, float)):
                    # Limit to 1-5 range, round to 1 decimal place
                    scores[metric] = round(max(1.0, min(5.0, float(val))), 1)
                else:
                    scores[metric] = 1.0

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