"""Editor Agent prompt and configuration."""

from crewai import Agent


class EditorAgent:
    """Editor Agent for revising drafts based on critique feedback."""

    @staticmethod
    def create() -> Agent:
        """Create the Editor Agent."""
        return Agent(
            role="Academic Writing Editor",
            goal="Revise academic drafts based on constructive criticism",
            backstory="""You are an experienced academic editor with a keen eye for detail. You can transform draft writing into polished academic work by incorporating feedback while maintaining the original author's voice and intent.""",
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def generate_prompt(
        instruction: str,
        source_material: str,
        draft: str,
        critique: str,
        target_word_count: int,
        rubric: dict,
    ) -> str:
        """Generate prompt for Editor Agent."""
        return f"""
        Task: Revise the following academic draft based on the provided critique.

        Writing Instruction:
        {instruction}

        Source Material:
        {source_material}

        Original Draft:
        {draft}

        Critique and Feedback:
        {critique}

        Target Word Count: {target_word_count} words

        Evaluation Rubric (ensure your revision meets these standards):
        {rubric}

        Revision Guidelines:
        1. Address all the weaknesses identified in the critique
        2. Implement the revision suggestions
        3. Maintain academic tone and style
        4. Keep the original argument intact while improving clarity
        5. Ensure proper use of evidence from source material
        6. Meet the target word count

        Please output only the revised final draft without any additional explanations or meta-commentary.
        """