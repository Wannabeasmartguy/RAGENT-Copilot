# from llama_cpp import Llama
from openai import OpenAI
from loguru import logger


class LLM:
    """
    LLM class encapsulates the logic to load a pre-trained language model and generate text based on input prompts.
    """

    def __init__(self) -> None:
        logger.info("Loading model...")
        self.system_prompt = (
            "You are responsible for rephrasing, summarizing, or editing various text snippets to make them more "
            "concise, coherent, and engaging. You are also responsible for writing emails, messages, and other forms "
            "of communication."
        )
        
        self.llm = OpenAI(
            base_url = 'http://localhost:11434/v1',
            api_key='noneed', # required, but unused
        )
        logger.info("Model loaded successfully.")

    def generate(
        self, text: str, max_tokens: int = 2048, temperature: float = 0.3
    ) -> str:
        """
        Generate a response from the language model based on the provided text.

        :param text: Input text prompt for the model.
        :param max_tokens: Maximum number of tokens to generate.
        :param temperature: Sampling temperature for generation.
        :return: Generated text response.
        """
        logger.info(f"Generating response for text: {text}")
        response = self.llm.chat.completions.create(
            model = "qwen2:latest",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        logger.info("response: {}".format(response))
        return response.choices[0].message.content
