"""Critic Agent prompt and configuration."""

from crewai import Agent


class CriticAgent:
    """Critic Agent for evaluating and providing feedback on drafts."""

    @staticmethod
    def create() -> Agent:
        """Create the Critic Agent."""
        return Agent(
            role="Academic Writing Critic",
            goal="Provide constructive criticism and actionable feedback on academic drafts",
            backstory="""You are a meticulous academic editor and reviewer with expertise in academic writing standards. You provide specific, actionable feedback to help writers improve their work while maintaining academic integrity and rigor.""",
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def generate_prompt(
        instruction: str,
        source_material: str,
        draft: str,
        rubric: dict,
    ) -> str:
        """Generate prompt for Critic Agent."""
        return f"""
        Task: Critique the following academic draft and provide actionable feedback.

        Writing Instruction:
        {instruction}

        Source Material:
        {source_material}

        Draft to Review:
        {draft}

        Evaluation Rubric (use this as your evaluation criteria):
        {rubric}

        Please provide your critique in the following structured format:

        ## Strengths
        - [Identify what works well in the draft]
        - [Another strength]
        ...

        ## Weaknesses
        - [Specific issue 1 with location/line reference if possible]
        - [Specific issue 2 with location/line reference if possible]
        ...

        ## Revision Suggestions
        - [Actionable suggestion for improvement]
        - [Actionable suggestion for improvement]
        ...

        ## Evidence Use Analysis
        - [How effectively is the source material being used?]
        - [What additional evidence could strengthen the argument?]

        Be specific and constructive. Focus on:
        - Relevance to the task
        - Structure and coherence
        - Evidence use and citation
        - Argument clarity
        - Academic style and tone
        - Grammar and readability
        """