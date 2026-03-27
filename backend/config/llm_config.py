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
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
}
