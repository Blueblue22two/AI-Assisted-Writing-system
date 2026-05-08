"""
Central orchestrator that controls the workflow for different experimental conditions.
Determines which agents run and in what order.
"""

import time
from typing import Any, Dict, Optional

from src.config import get_config
from src.environment import SharedWorkspace

# Import CrewFactory - this will be implemented by the Multi-Agent engineer
# We use a try/except to allow for incremental development
try:
    from src.crew_factory import CrewFactory
except ImportError:
    # Placeholder for when crew_factory is not yet available
    CrewFactory = None  # type: ignore


class Orchestrator:
    """
    Deterministic workflow controller.
    Executes different agent chains based on experimental condition.
    """

    def __init__(self) -> None:
        """Initialize orchestrator with configuration and crew factory."""
        self.config = get_config()
        if CrewFactory is None:
            raise ImportError(
                "CrewFactory not found. Ensure src/crew_factory.py is implemented."
            )
        self.crew_factory = CrewFactory()

    def run_single_agent_baseline(self, workspace: SharedWorkspace) -> SharedWorkspace:
        """
        Condition A: Single Writer Agent generates final answer directly.

        Args:
            workspace: Shared workspace with task data.

        Returns:
            Updated workspace with final_answer.
        """
        start_time = time.time()

        # Create and run the single-agent crew
        crew = self.crew_factory.create_single_agent_crew(workspace)
        result = crew.kickoff()

        # Extract final answer - CrewAI typically returns result as string
        workspace.final_answer = str(result)
        workspace.condition = "baseline"
        workspace.runtime_seconds = time.time() - start_time

        return workspace

    def run_plan_execute(self, workspace: SharedWorkspace) -> SharedWorkspace:
        """
        Condition B: Planner -> Writer.

        Args:
            workspace: Shared workspace with task data.

        Returns:
            Updated workspace with plan and final_answer.
        """
        start_time = time.time()

        crew = self.crew_factory.create_plan_execute_crew(workspace)
        result = crew.kickoff()

        workspace.final_answer = str(result)
        workspace.condition = "plan_execute"
        workspace.runtime_seconds = time.time() - start_time

        # Note: plan is written to workspace by the Planner agent via the crew's shared memory
        return workspace

    def run_plan_execute_critique(self, workspace: SharedWorkspace) -> SharedWorkspace:
        """
        Condition C: Planner -> Writer -> Critic -> Editor.

        Args:
            workspace: Shared workspace with task data.

        Returns:
            Updated workspace with plan, draft, critique, and final_answer.
        """
        start_time = time.time()

        crew = self.crew_factory.create_plan_execute_critique_crew(workspace)
        result = crew.kickoff()

        workspace.final_answer = str(result)
        workspace.condition = "plan_execute_critique"
        workspace.runtime_seconds = time.time() - start_time

        return workspace

    def run_condition(
        self, workspace: SharedWorkspace, condition: str
    ) -> SharedWorkspace:
        """
        Run the specified experimental condition.

        Args:
            workspace: Shared workspace with task data.
            condition: One of "baseline", "plan_execute", or "plan_execute_critique".

        Returns:
            Updated workspace with results.

        Raises:
            ValueError: If condition is unknown.
        """
        condition_map = {
            "baseline": self.run_single_agent_baseline,
            "plan_execute": self.run_plan_execute,
            "plan_execute_critique": self.run_plan_execute_critique,
        }

        if condition not in condition_map:
            raise ValueError(f"Unknown condition: {condition}")

        # Set condition and repetition_id before run
        workspace.condition = condition

        # Run the workflow
        return condition_map[condition](workspace)