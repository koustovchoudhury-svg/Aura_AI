import os
import requests

def _ollama_available(base_url: str, model: str) -> bool:
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=2)
        resp.raise_for_status()
        tags = [m.get("name", "") for m in resp.json().get("models", [])]
        return any(t == model or t.startswith(model.split(":")[0]) for t in tags)
    except Exception:
        return False

def _nvidia_llm(model: str = None, temperature: float = 0.2):
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=model or os.getenv("NVIDIA_LLM_MODEL", "google/gemma-3n-e2b-it"),
        api_key=os.getenv("NVIDIA_API_KEY"),
        base_url="https://integrate.api.nvidia.com/v1",
        temperature=temperature,
        max_tokens=512,
        top_p=0.70,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

def get_llm(prefer_local: bool = True, model: str = None):
    base_url   = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    local_model = model or os.getenv("DEFAULT_LOCAL_MODEL", "llama3.2:3b")

    if prefer_local and _ollama_available(base_url, local_model):
        from langchain_community.chat_models import ChatOllama
        return ChatOllama(model=local_model, base_url=base_url, temperature=0.7)

    if os.getenv("NVIDIA_API_KEY"):
        return _nvidia_llm(model, temperature=0.2)

    if os.getenv("ANTHROPIC_API_KEY"):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model or os.getenv("DEFAULT_CLOUD_MODEL", "claude-sonnet-4-6"),
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0.7, max_tokens=4096
        )

    if os.getenv("OPENAI_API_KEY"):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.7
        )

    from langchain_community.chat_models import ChatOllama
    return ChatOllama(model=local_model, base_url=base_url, temperature=0.7)
