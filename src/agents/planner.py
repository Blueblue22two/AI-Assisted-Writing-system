"""Planner Agent prompt and configuration."""

from crewai import Agent


class PlannerAgent:
    """Planner Agent for generating writing plans."""

    @staticmethod
    def create() -> Agent:
        """Create the Planner Agent."""
        return Agent(
            role="Academic Writing Planner",
            goal="Generate a comprehensive writing plan for academic tasks",
            backstory="""You are an expert academic writing advisor with extensive experience in helping students and researchers structure their academic papers. You excel at analyzing writing instructions, identifying key arguments, and creating structured outlines that maximize clarity and academic rigor.""",
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def generate_prompt(
        instruction: str,
        source_material: str,
        target_word_count: int,
        rubric: dict,
    ) -> str:
        """Generate prompt for Planner Agent."""
        return f"""
        Task: Write a detailed academic writing plan for the following assignment.

        Writing Instruction:
        {instruction}

        Source Material:
        {source_material}

        Target Word Count: {target_word_count} words

        Evaluation Rubric (use this as guidance for quality):
        {rubric}

        Please provide your plan in the following structured format:

        ## Thesis Statement
        [Your central argument or main claim that the writing will support]

        ## Paragraph Outline
        1. [Purpose and content of paragraph 1]
        2. [Purpose and content of paragraph 2]
        3. [Purpose and content of paragraph 3]
        ... (continue as needed)

        ## Key Arguments
        - [Argument 1: What point will you make?]
        - [Argument 2: What point will you make?]
        - [Argument 3: What point will you make?]
        ...

        ## Evidence Plan
        - [Which evidence from source material supports Argument 1?]
        - [Which evidence from source material supports Argument 2?]
        - [Any additional evidence or examples needed?]

        ## Writing Strategy
        [Brief notes on tone, style, and approach to meet academic standards]

        Ensure your plan directly addresses the writing instruction and uses the source material effectively.
        """