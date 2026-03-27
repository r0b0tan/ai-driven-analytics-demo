import os

# Default provider — overridden at runtime via /api/llm/provider
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.2:latest")

# Ollama endpoint (default for WSL)
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Available model options surfaced to the UI
PROVIDER_MODELS = {
    "ollama": ["llama3.2:latest", "llama3.1:8b", "mistral:latest"],
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "qwen/qwen3-32b",
        "openai/gpt-oss-120b",
    ],
}
