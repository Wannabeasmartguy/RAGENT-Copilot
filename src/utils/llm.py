# from llama_cpp import Llama
from openai import OpenAI
from loguru import logger
from utils.logger_config import setup_logger

from typing import List


DEFAULT_MODEL = "qwen2:1.5b"
DEFAULT_CONFIG = [
    {
        "model": DEFAULT_MODEL,
        "api_key": "noneed",
        "base_url": "http://localhost:11434/v1",
        "params": {
            "temperature": 0.3,
            "top_p": 0.5,
            "max_tokens": 2048,
            "stream": False,
        },
    }
]


class LLM:
    """
    LLM class encapsulates the logic to load a pre-trained language model and generate text based on input prompts.
    """

    def __init__(self, config_list: List = DEFAULT_CONFIG) -> None:
        logger.info("Loading model...")
        self.config_list = config_list
        self.defult_config = config_list[0]
        self.system_prompt = (
            "You are responsible for rephrasing, summarizing, or editing various text snippets to make them more "
            "concise, coherent, and engaging. You are also responsible for writing emails, messages, and other forms "
            "of communication."
        )
        
        self.llm = OpenAI(
            base_url = self.defult_config["base_url"],
            api_key = self.defult_config["api_key"], 
        )
        logger.info("Model loaded successfully.")

    def generate(
        self, text: str
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
            model = self.defult_config["model"],
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=self.defult_config["params"]["temperature"],
            max_tokens=self.defult_config["params"]["max_tokens"],
            stream=self.defult_config["params"]["stream"],
        )
        if self.defult_config["params"]["stream"]:
            logger.info("Streaming response")
            return response
        else:
            logger.info("Response: {}".format(response))
            return response.choices[0].message.content