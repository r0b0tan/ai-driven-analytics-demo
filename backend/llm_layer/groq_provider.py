import os
import re
from .base_provider import BaseLLMProvider


class GroqProvider(BaseLLMProvider):

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq package not installed. Run: pip install groq")

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        return re.sub(r"<think>.*?</think>\s*", "", content, flags=re.DOTALL)
