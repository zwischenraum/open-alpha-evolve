import re
from typing import List
from copy import deepcopy


class Program:
    """
    Represents a program to be evolved, with evolvable blocks.
    """

    EVOLVE_BLOCK_START = "# EVOLVE-BLOCK-START"
    EVOLVE_BLOCK_END = "# EVOLVE-BLOCK-END"

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.code: str = ""
        self.evolve_blocks: List[str] = []
        self._skeleton: List[str] = []
        self._load_and_parse()

    def _load_and_parse(self):
        """Loads the program from the file and parses it into skeleton and evolvable blocks."""
        try:
            with open(self.file_path, "r") as f:
                self.code = f.read()
        except FileNotFoundError:
            # This can happen if we are creating a new program from a diff
            # The code content will be set by the caller.
            pass

        parts = self.code.split(self.EVOLVE_BLOCK_START)
        self._skeleton.append(parts[0])

        for i in range(1, len(parts)):
            block_and_rest = parts[i].split(self.EVOLVE_BLOCK_END)
            if len(block_and_rest) != 2:
                raise ValueError(f"Mismatched EVOLVE-BLOCK markers in {self.file_path}")

            evolve_block, skeleton_part = block_and_rest
            # We keep the surrounding newlines for the diff
            self.evolve_blocks.append(evolve_block)
            self._skeleton.append(skeleton_part)

    def __str__(self) -> str:
        """Reconstructs the full code from the skeleton and evolve blocks."""
        reconstructed_code = self._skeleton[0]
        for i, evolve_block in enumerate(self.evolve_blocks):
            reconstructed_code += self.EVOLVE_BLOCK_START
            reconstructed_code += evolve_block
            reconstructed_code += self.EVOLVE_BLOCK_END
            reconstructed_code += self._skeleton[i + 1]
        return reconstructed_code

    def apply_diff(self, diff_str: str) -> "Program":
        """
        Applies a diff in the SEARCH/REPLACE format to the program's evolve blocks.
        This version is more robust as it operates on blocks, not the whole file.
        """
        new_program = deepcopy(self)

        search_pattern = r"<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE"
        matches = re.finditer(search_pattern, diff_str, re.DOTALL)

        for match in matches:
            search_block = match.group(1)
            replace_block = match.group(2)

            found_and_replaced = False
            for i, evolve_block in enumerate(new_program.evolve_blocks):
                if search_block in evolve_block:
                    new_program.evolve_blocks[i] = evolve_block.replace(
                        search_block, replace_block
                    )
                    found_and_replaced = True
                    break  # Move to the next diff match

            if not found_and_replaced:
                print("Warning: Could not find SEARCH block in any evolve_block.")
                # We could decide to discard the whole mutation, but for now we'll allow partial application.

        # Update the full code string of the new program object
        new_program.code = str(new_program)
        return new_program
