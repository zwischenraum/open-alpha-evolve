import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class LLMGenerator:
    """
    Interacts with a remote LLM API via the OpenAI SDK to generate code modifications.
    """

    def __init__(self, model_name: str = None):
        """
        Initializes the generator.
        The model can be specified or loaded from the MODEL_ID environment variable.
        """
        default_model = os.getenv("MODEL_ID", "google/gemini-flash-1.5")
        self.model_name = model_name if model_name is not None else default_model
        self.client = self._configure_api()

    def _configure_api(self) -> OpenAI:
        """Configures the OpenAI client using environment variables."""
        api_key = os.getenv("API_KEY")
        base_url = os.getenv("BASE_URL")

        if not api_key:
            raise ValueError(
                "API_KEY environment variable not set. Please create a .env file."
            )
        if not base_url:
            raise ValueError(
                "BASE_URL environment variable not set. Please create a .env file."
            )

        return OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def generate(self, prompt: str) -> str:
        """
        Generates a response from the LLM given a prompt.

        Args:
            prompt: The full prompt to send to the model.

        Returns:
            The generated text content from the model.
        """
        try:
            print(
                f"Sending prompt to LLM ({self.model_name}) via {self.client.base_url}..."
            )
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
            )
            print("Received response from LLM.")
            return response.choices[0].message.content
        except Exception as e:
            print(f"An error occurred while calling the API: {e}")
            return ""  # Return empty string on error
