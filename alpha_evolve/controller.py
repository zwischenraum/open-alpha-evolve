from .database import ProgramDatabase
from .evaluator import Evaluator
from .generator import LLMGenerator
from .program import Program
from .prompt import PromptSampler, get_default_system_prompt


class AlphaEvolveController:
    """
    Orchestrates the main evolutionary loop of the AlphaEvolve algorithm.
    """

    def __init__(self, initial_program_path: str, eval_script_path: str):
        # Initialize the core components
        self.database = ProgramDatabase()
        self.evaluator = Evaluator(eval_script_path)
        self.generator = LLMGenerator()

        system_prompt = get_default_system_prompt()
        self.prompt_sampler = PromptSampler(system_prompt)

        # Load the initial program and add it to the database
        self._initialize_population(initial_program_path)

    def _initialize_population(self, program_path: str):
        """
        Initializes the population with the seed program.
        """
        print("Initializing population...")
        initial_program = Program(program_path)

        print("Evaluating initial program...")
        scores = self.evaluator.execute(initial_program)

        if "error" in scores:
            raise RuntimeError(f"Failed to evaluate initial program: {scores['error']}")

        self.database.add(initial_program, scores)
        print("Initialization complete.")

    def run_evolution(self, generations: int = 10):
        """
        Runs the main evolutionary loop for a given number of generations.
        """
        print("Starting evolution...")
        for i in range(generations):
            print(f"\n--- Generation {i+1}/{generations} ---")

            # 1. Sample a parent program and its scores
            parent_item = self.database.sample()
            if not parent_item:
                print("No programs in database to evolve. Stopping.")
                break
            parent_program, parent_scores = parent_item
            print(
                f"Selected parent program: {parent_program.file_path} with scores {parent_scores}"
            )

            # 2. Get inspirations (program, scores)
            inspirations = self.database.get_inspirations()

            # 3. Build the prompt, including scores
            prompt = self.prompt_sampler.build_prompt(
                (parent_program, parent_scores), inspirations
            )

            # 4. Generate a diff
            diff_str = self.generator.generate(prompt)
            if not diff_str:
                print("LLM failed to generate a diff. Skipping generation.")
                continue

            print(f"Generated diff:\n{diff_str}")

            # 5. Apply the diff to create a child program
            child_program = parent_program.apply_diff(diff_str)

            # 6. Evaluate the new program
            print("Evaluating child program...")
            scores = self.evaluator.execute(child_program)

            # 7. Add the new program to the database if it's valid
            if "error" not in scores:
                self.database.add(child_program, scores)
            else:
                print("Child program failed evaluation. Discarding.")

        print("\nEvolution finished.")
        # Print the best result
        best_program = self.database.sample()
        if best_program:
            print(
                f"Best program found stored in a temporary file: {best_program.file_path}"
            )
