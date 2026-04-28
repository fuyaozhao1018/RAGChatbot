import os
import asyncio
from functools import lru_cache
import httpx

from config import load_project_env

load_project_env()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "llama_cpp_server").strip().lower()
LLM_API_BASE = os.getenv("LLM_API_BASE", "http://localhost:8001/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3-8b-instruct")
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLAMA_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH", "").strip()
LLAMA_N_CTX = int(os.getenv("LLAMA_N_CTX", "4096"))
LLAMA_N_GPU_LAYERS = int(os.getenv("LLAMA_N_GPU_LAYERS", "-1"))


@lru_cache(maxsize=1)
def get_llama_cpp_model():
    if not LLAMA_MODEL_PATH:
        raise RuntimeError("LLAMA_MODEL_PATH is required when LLM_PROVIDER=llama_cpp")
    try:
        from llama_cpp import Llama
    except ImportError as exc:
        raise RuntimeError(
            "llama-cpp-python is not installed. Run: pip install llama-cpp-python"
        ) from exc
    return Llama(
        model_path=LLAMA_MODEL_PATH,
        n_ctx=LLAMA_N_CTX,
        n_gpu_layers=LLAMA_N_GPU_LAYERS,
        verbose=False,
    )


async def chat_completion_llama_cpp(
    messages,
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> str:
    """
    Loads a local GGUF model directly with llama-cpp-python.
    """
    model = get_llama_cpp_model()

    def run_completion():
        response = model.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response["choices"][0]["message"]["content"]

    return await asyncio.to_thread(run_completion)


async def chat_completion_server(
    messages,
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> str:
    """
    Calls a local OpenAI-compatible /v1/chat/completions endpoint
    such as llama.cpp's llama-server or vLLM.
    """
    url = f"{LLM_API_BASE}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if LLM_API_KEY:
        headers["Authorization"] = f"Bearer {LLM_API_KEY}"
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]


async def chat_completion(messages, temperature: float = 0.2, max_tokens: int = 512) -> str:
    if LLM_PROVIDER == "llama_cpp":
        return await chat_completion_llama_cpp(messages, temperature, max_tokens)
    return await chat_completion_server(messages, temperature, max_tokens)
