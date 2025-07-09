from typing import List, Dict, Tuple, Optional
from .program import Program


class ProgramDatabase:
    """
    Stores the population of programs and their scores.
    """

    def __init__(self):
        # A simple list to store tuples of (program, scores)
        # In a real system, this could be a more sophisticated structure.
        self.programs: List[Tuple[Program, Dict[str, float]]] = []
        self._primary_metric = "average_score"  # Default, can be configured

    def add(self, program: Program, scores: Dict[str, float]):
        """Adds a program and its scores to the database."""
        # For now, just append. Could have logic to avoid duplicates.
        self.programs.append((program, scores))
        print(f"Added program from {program.file_path} with scores: {scores}")

    def set_primary_metric(self, metric: str):
        """Set the primary metric to optimize for."""
        self._primary_metric = metric

    def sample(self) -> Optional[Tuple[Program, Dict[str, float]]]:
        """
        Samples a (program, scores) tuple to be the parent for a new generation.
        A simple strategy: pick the one with the best score on the primary metric.
        """
        if not self.programs:
            return None

        sorted_programs = sorted(
            self.programs,
            key=lambda item: item[1].get(self._primary_metric, -float("inf")),
            reverse=True,
        )
        return sorted_programs[0]

    def get_inspirations(self, n: int = 3) -> List[Tuple[Program, Dict[str, float]]]:
        """
        Gets a list of (program, scores) tuples for diverse, high-performing inspirations.

        Simple strategy: return the top n entries, excluding the very best one.
        """
        if len(self.programs) <= 1:
            return []

        sorted_programs = sorted(
            self.programs,
            key=lambda item: item[1].get(self._primary_metric, -float("inf")),
            reverse=True,
        )
        # Return the next best n items after the top one
        return sorted_programs[1 : n + 1]
