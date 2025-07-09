import multiprocessing
import importlib.util
import time
from typing import Dict
import sys

from .program import Program

# -----------------------------------------------------------------------------
# Evaluator
# -----------------------------------------------------------------------------


class Evaluator:
    """
    Evaluates a program in a separate, sandboxed process to get its performance scores.
    """

    def __init__(self, eval_script_path: str, timeout: int = 300):
        """
        Args:
            eval_script_path: Path to the evaluation script.
            timeout: Maximum time in seconds to allow for an evaluation.
        """
        self.eval_script_path = eval_script_path
        self.timeout = timeout

    def execute(self, program: Program) -> Dict[str, float]:
        """
        Executes the 'evaluate' function of a given program.

        Args:
            program: The Program object to evaluate.

        Returns:
            A dictionary of scores, or an empty dict if an error occurs.
        """
        result_queue = multiprocessing.Queue()

        # We need to save the current state of the program to a temporary file
        # for the subprocess to execute. A robust implementation might use a
        # dedicated directory for these temporary evaluation files.
        temp_program_path = f"/tmp/candidate_{time.time_ns()}.py"
        with open(temp_program_path, "w") as f:
            f.write(str(program))

        process = multiprocessing.Process(
            target=self._worker_wrapper, args=(temp_program_path, result_queue)
        )

        process.start()
        process.join(timeout=self.timeout)

        if process.is_alive():
            process.terminate()
            process.join()
            print("Evaluation timed out.")
            return {"error": "timeout"}

        if result_queue.empty():
            print("Evaluation failed with no result.")
            return {"error": "no_result"}

        result = result_queue.get()
        if "error" in result:
            print(f"Evaluation failed with error: {result['error']}")
            return result

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _worker_wrapper(self, candidate_path: str, queue: multiprocessing.Queue):
        """Runs in the child process: loads candidate as module 'candidate' then eval script."""
        try:
            # ------------------------------------------------------------------
            # 1. Dynamically load the candidate program as module name 'candidate'
            # ------------------------------------------------------------------
            spec_candidate = importlib.util.spec_from_file_location(
                "candidate", candidate_path
            )
            candidate_module = importlib.util.module_from_spec(spec_candidate)
            sys.modules["candidate"] = (
                candidate_module  # So evaluation can `import candidate`
            )
            spec_candidate.loader.exec_module(candidate_module)

            # ------------------------------------------------------------------
            # 2. Dynamically load the evaluation script
            # ------------------------------------------------------------------
            spec_eval = importlib.util.spec_from_file_location(
                "evaluation", self.eval_script_path
            )
            eval_module = importlib.util.module_from_spec(spec_eval)
            spec_eval.loader.exec_module(eval_module)

            if not hasattr(eval_module, "evaluate"):
                raise AttributeError(
                    "Evaluation script must define an 'evaluate' function"
                )

            scores = eval_module.evaluate()

            if not isinstance(scores, dict):
                raise TypeError("'evaluate' must return dict")

            queue.put(scores)

        except Exception as exc:
            queue.put({"error": str(exc)})
