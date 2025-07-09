# Open AlphaEvolve

This repository contains an implementation of the [AlphaEvolve](https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/AlphaEvolve.pdf) algorithm.

## Getting Started

Follow these instructions to set up the project locally.

### Prerequisites

- Python 3.12+
- `uv` installed. You can install it with:
  ```bash
  pip install uv
  ```

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/zwischenraum/open-alpha-evolve.git
    cd open-alpha-evolve
    ```

2.  **Create a virtual environment and install dependencies:**
    Use `uv` to create a virtual environment and install the required packages.
    ```bash
    uv sync
    ```

3.  **Set up pre-commit hooks:**
    This project uses `ruff` for linting and formatting, managed by `pre-commit`.
    Install `pre-commit` and set up the hooks:
    ```bash
    pip install pre-commit
    pre-commit install
    ```
    The hooks will now run automatically on every commit.

## Usage

To run AlphaEvolve, you need to provide an initial program and an evaluation script.

```bash
python main.py <path_to_initial_program> <path_to_evaluation_script> --generations <num_generations>
```

-   `<path_to_initial_program>`: Path to the Python file containing the initial code to be evolved.
-   `<path_to_evaluation_script>`: Path to the Python script that evaluates the fitness of a program.
-   `--generations` (optional): The number of generations to run the evolution for (default is 5).

### Example

The repository includes a sample problem. You can run it with:

```bash
uv run main.py problem.py evaluate.py
```

## How to Define a Problem

To use AlphaEvolve on your own problem, you need to create two files:

### 1. The Initial Program

This is a Python file that contains the initial code you want to evolve. You must mark the section of the code that the LLM is allowed to modify using `EVOLVE-BLOCK-START` and `EVOLVE-BLOCK-END` comments.

**Example: `problem.py`**

```python
"""
This is a simple problem for AlphaEvolve to solve.
"""

# EVOLVE-BLOCK-START
def get_magic_number():
    """This function should be evolved to return a number."""
    return 0
# EVOLVE-BLOCK-END
```

### 2. The Evaluation Script

This is a Python script that evaluates the fitness of a given program. It should contain a function called `evaluate()` that returns a dictionary of scores. The program being evaluated will be available to this script as a module named `candidate`.

**Example: `evaluate.py`**

This script tries to evolve the `get_magic_number` function to return the number `42`.

```python
from candidate import get_magic_number

def evaluate():
    """
    Calculates the fitness of the candidate program.
    The score is the negative absolute difference between the magic number and 42.
    A score of 0 is a perfect score.
    """
    score = -abs(42 - get_magic_number())
    return {"average_score": score}
```

The evaluation function can return multiple metrics to track different aspects of performance. Common metrics include:

- **average_score**: Overall performance metric
- **runtime**: Execution time in seconds
- **memory_usage**: Memory consumption in bytes
- **error_rate**: Percentage of failed operations
- **latency**: Response time for individual operations
- **accuracy**: Percentage of correct predictions or outputs
