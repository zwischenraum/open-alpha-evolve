from typing import List, Tuple, Dict
from .program import Program


class PromptSampler:
    """
    Constructs prompts for the LLM based on programs from the database.
    """

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def build_prompt(
        self,
        current: Tuple[Program, Dict[str, float]],
        inspirations: List[Tuple[Program, Dict[str, float]]],
    ) -> str:
        """
        Builds a rich prompt for the LLM to generate a new program version,
        including program scores to inform the model of past performance.
        """
        prompt = self.system_prompt + "\n\n"

        # Add inspirations with their scores
        if inspirations:
            prompt += "- Prior programs and scores\n"
            prompt += (
                "Previously we found that the following programs performed well:\n"
            )
            for prog, scores in inspirations:
                prompt += f"Code:\n```\n{str(prog)}\n```\nScore: {scores}\n\n"
            prompt += "\n"

        # Add the current program and its score
        cur_prog, cur_scores = current
        prompt += "- Current program and score\n"
        prompt += "Here is the current program to improve (scores shown below):\n"
        prompt += f"Code:\n```\n{str(cur_prog)}\n```\nScore: {cur_scores}\n\n"

        # Add instructions for the output
        prompt += "Task: Suggest a new idea to improve the code that is inspired by your expert knowledge.\n"
        prompt += "Describe each change with a SEARCH/REPLACE block. For example:\n"
        prompt += """
<<<<<<< SEARCH
# Original code block to be found
=======
# and replaced
# New code block to replace the original
>>>>>>> REPLACE
"""
        return prompt


def get_default_system_prompt() -> str:
    """Returns a default system prompt for the code evolution task."""
    return """Act as an expert software developer. Your task is to iteratively improve the provided codebase.
You will be given a program to improve, along with examples of previously successful programs.
Propose a single, targeted modification to the "Current program". Your goal is to improve its performance based on the problem description.
Higher scores are always better (e.g. 10 is better than 0, which is better than -10).
Think step-by-step about what could be improved.
Your output must be a diff in the specified SEARCH/REPLACE format.
"""
