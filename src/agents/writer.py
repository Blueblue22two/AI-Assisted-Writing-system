"""Writer Agent prompt and configuration."""

from crewai import Agent


class WriterAgent:
    """Writer Agent for generating academic drafts."""

    @staticmethod
    def create() -> Agent:
        """Create the Writer Agent."""
        return Agent(
            role="Academic Writer",
            goal="Generate high-quality academic drafts based on provided plans",
            backstory="""You are a skilled academic writer with expertise in various disciplines. You produce well-researched, structured, and academically rigorous writing. You follow instructions carefully and maintain appropriate academic tone.""",
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def generate_prompt(
        instruction: str,
        source_material: str,
        writing_plan: str,
        target_word_count: int,
        rubric: dict,
    ) -> str:
        """Generate prompt for Writer Agent."""
        return f"""
        Task: Write an academic draft according to the provided writing plan.

        Writing Instruction:
        {instruction}

        Source Material:
        {source_material}

        Writing Plan:
        {writing_plan}

        Target Word Count: {target_word_count} words

        Evaluation Rubric (ensure your writing meets these standards):
        {rubric}

        Requirements:
        - Write in a formal academic tone
        - Use evidence from the source material to support your arguments
        - Follow the structure outlined in the writing plan
        - Maintain logical flow and coherence
        - Avoid plagiarism - properly integrate source material
        - Meet the target word count

        Please output only the academic draft without any additional explanations or meta-commentary.
        """