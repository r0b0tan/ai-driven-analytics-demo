import requests
from .base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, messages: list[dict]) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def list_models(self) -> list[str]:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            return [m["name"] for m in response.json().get("models", [])]
        except Exception:
            return []

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except Exception:
            return False
