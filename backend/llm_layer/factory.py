from .base_provider import BaseLLMProvider

# Runtime state — mutable so the API can switch providers without restart
_current_provider: str = "ollama"
_current_model: str = "llama3"
_instance: BaseLLMProvider | None = None


def set_provider(provider: str, model: str) -> None:
    global _current_provider, _current_model, _instance
    _current_provider = provider
    _current_model = model
    _instance = None  # Force re-instantiation on next get_llm() call


def get_llm() -> BaseLLMProvider:
    global _instance
    if _instance is not None:
        return _instance

    if _current_provider == "groq":
        from .groq_provider import GroqProvider
        _instance = GroqProvider(model=_current_model)
    elif _current_provider == "ollama":
        from .ollama_provider import OllamaProvider
        _instance = OllamaProvider(model=_current_model)
    else:
        raise ValueError(f"Unknown LLM provider: {_current_provider!r}")

    return _instance


def get_provider_info() -> dict:
    return {
        "provider": _current_provider,
        "model": _current_model,
    }
