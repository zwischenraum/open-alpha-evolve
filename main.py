import argparse
from alpha_evolve.controller import AlphaEvolveController


def setup_tracing():
    import os
    from phoenix.otel import register
    from openinference.instrumentation.openai import OpenAIInstrumentor

    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = "http://localhost:6006"

    tracer_provider = register(
        project_name="alpha-evolve",
    )

    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)


def main():
    """
    Main entry point for running the AlphaEvolve algorithm.
    """
    parser = argparse.ArgumentParser(description="Run the AlphaEvolve algorithm.")
    parser.add_argument(
        "program_path", type=str, help="Path to the initial program file to be evolved."
    )
    parser.add_argument(
        "eval_script_path", type=str, help="Path to the evaluation script file."
    )
    parser.add_argument(
        "--generations",
        type=int,
        default=5,
        help="Number of generations to run the evolution for.",
    )
    args = parser.parse_args()

    # setup_tracing()

    try:
        controller = AlphaEvolveController(
            initial_program_path=args.program_path,
            eval_script_path=args.eval_script_path,
        )
        controller.run_evolution(generations=args.generations)
    except Exception as e:
        print(f"An error occurred during evolution: {e}")


if __name__ == "__main__":
    main()
