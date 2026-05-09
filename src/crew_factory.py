"""Factory helpers for creating CrewAI agents, tasks, and crews."""

from typing import Optional

from crewai import Agent, Crew, Task
from crewai.process import Process

from src.agents.critic import CriticAgent
from src.agents.editor import EditorAgent
from src.agents.planner import PlannerAgent
from src.agents.writer import WriterAgent
from src.config import LLMConfig, WritingTask


class CrewFactory:
    """Factory for creating CrewAI crews for different experimental conditions."""

    def __init__(self, llm_config: LLMConfig, api_key: str):
        self.llm_config = llm_config
        self.api_key = api_key
        self._setup_llm()

    def _setup_llm(self):
        """Configure LLM for CrewAI agents."""
        from crewai import LLM
        self.llm = LLM(
            model=self.llm_config.default_model,
            base_url=self.llm_config.base_url,
            api_key=self.api_key,
            temperature=self.llm_config.temperature,
            max_tokens=self.llm_config.max_tokens,
        )

    def _create_planner_agent(self) -> Agent:
        """Create and configure Planner agent."""
        planner = PlannerAgent.create()
        planner.llm = self.llm
        return planner

    def _create_writer_agent(self) -> Agent:
        """Create and configure Writer agent."""
        writer = WriterAgent.create()
        writer.llm = self.llm
        return writer

    def _create_critic_agent(self) -> Agent:
        """Create and configure Critic agent."""
        critic = CriticAgent.create()
        critic.llm = self.llm
        return critic

    def _create_editor_agent(self) -> Agent:
        """Create and configure Editor agent."""
        editor = EditorAgent.create()
        editor.llm = self.llm
        return editor

    def create_single_agent_crew(self, task: WritingTask) -> Crew:
        """
        Create a single-agent baseline crew.

        Condition A: Single-Agent Baseline
        One writer agent directly generates the final answer.
        """
        writer = self._create_writer_agent()

        write_task = Task(
            description=WriterAgent.generate_prompt(
                instruction=task.instruction,
                source_material=task.source_material,
                writing_plan="",
                target_word_count=task.target_word_count,
                rubric=task.rubric.model_dump(),
            ),
            agent=writer,
            expected_output="A complete academic essay meeting the task requirements (approximately 800 words).",
        )

        return Crew(
            agents=[writer],
            tasks=[write_task],
            process=Process.sequential,
            verbose=True,
            tracing=False,
        )

    def create_plan_execute_crew(self, task: WritingTask) -> Crew:
        """
        Create a plan-execute crew.

        Condition B: Plan-Execute
        Planner -> Writer
        """
        planner = self._create_planner_agent()
        writer = self._create_writer_agent()

        plan_task = Task(
            description=PlannerAgent.generate_prompt(
                instruction=task.instruction,
                source_material=task.source_material,
                target_word_count=task.target_word_count,
                rubric=task.rubric.model_dump(),
            ),
            agent=planner,
            expected_output="""A detailed writing plan with:
            - Thesis statement
            - Detailed paragraph outline with topic sentences
            - Key arguments in order
            - Evidence plan mapping source material to arguments
            - Writing strategy notes""",
        )

        write_task = Task(
            description=WriterAgent.generate_prompt(
                instruction=task.instruction,
                source_material=task.source_material,
                writing_plan="{plan_task.output}",
                target_word_count=task.target_word_count,
                rubric=task.rubric.model_dump(),
            ),
            agent=writer,
            expected_output="A complete academic essay following the writing plan (approximately 800 words).",
            context=[plan_task],
        )

        return Crew(
            agents=[planner, writer],
            tasks=[plan_task, write_task],
            process=Process.sequential,
            verbose=True,
            tracing=False,
        )

    def create_plan_execute_critique_crew(self, task: WritingTask) -> Crew:
        """
        Create a plan-execute-critique crew.

        Condition C: Plan-Execute-Critique
        Planner -> Writer -> Critic -> Editor
        """
        planner = self._create_planner_agent()
        writer = self._create_writer_agent()
        critic = self._create_critic_agent()
        editor = self._create_editor_agent()

        plan_task = Task(
            description=PlannerAgent.generate_prompt(
                instruction=task.instruction,
                source_material=task.source_material,
                target_word_count=task.target_word_count,
                rubric=task.rubric.model_dump(),
            ),
            agent=planner,
            expected_output="""A detailed writing plan with:
            - Thesis statement
            - Detailed paragraph outline with topic sentences
            - Key arguments in order
            - Evidence plan mapping source material to arguments
            - Writing strategy notes""",
        )

        write_task = Task(
            description=WriterAgent.generate_prompt(
                instruction=task.instruction,
                source_material=task.source_material,
                writing_plan="{plan_task.output}",
                target_word_count=task.target_word_count,
                rubric=task.rubric.model_dump(),
            ),
            agent=writer,
            expected_output="A complete academic draft following the writing plan (approximately 800 words).",
            context=[plan_task],
        )

        critique_task = Task(
            description=CriticAgent.generate_prompt(
                instruction=task.instruction,
                source_material=task.source_material,
                draft="{write_task.output}",
                rubric=task.rubric.model_dump(),
            ),
            agent=critic,
            expected_output="""A structured critique with:
            - Summary assessment
            - Dimension-by-dimension feedback (relevance, structure, evidence use, argument clarity, academic style, grammar)
            - Specific revision suggestions
            - Priority revision checklist""",
            context=[write_task],
        )

        edit_task = Task(
            description=EditorAgent.generate_prompt(
                instruction=task.instruction,
                source_material=task.source_material,
                draft="{write_task.output}",
                critique="{critique_task.output}",
                target_word_count=task.target_word_count,
                rubric=task.rubric.model_dump(),
            ),
            agent=editor,
            expected_output="A revised final academic essay addressing all critique points (approximately 800 words).",
            context=[write_task, critique_task],
        )

        return Crew(
            agents=[planner, writer, critic, editor],
            tasks=[plan_task, write_task, critique_task, edit_task],
            process=Process.sequential,
            verbose=True,
            tracing=False,
        )

    def get_crew_for_condition(self, condition: str, task: WritingTask) -> Crew:
        """
        Get the appropriate crew for a given experimental condition.

        Args:
            condition: One of "single_agent", "plan_execute", "plan_execute_critique"
            task: The writing task to execute

        Returns:
            A CrewAI Crew configured for the specified condition

        Raises:
            ValueError: If condition is not recognized
        """
        condition_map = {
            "single_agent": self.create_single_agent_crew,
            "plan_execute": self.create_plan_execute_crew,
            "plan_execute_critique": self.create_plan_execute_critique_crew,
        }

        if condition not in condition_map:
            raise ValueError(f"Unknown condition: {condition}. Must be one of: {list(condition_map.keys())}")

        return condition_map[condition](task)

    @staticmethod
    def list_conditions() -> list[str]:
        """Return list of available experimental conditions."""
        return ["single_agent", "plan_execute", "plan_execute_critique"]