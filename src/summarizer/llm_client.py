"""Cliente LLM que abstrae Ollama y permite fallback a APIs externas."""

import requests
import json


def load_model(model: str = "mistral:latest") -> None:
    """Precarga el modelo en Ollama para que esté listo cuando se necesite."""
    try:
        requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": "", "keep_alive": "10m"},
            timeout=60,
        )
        print(f"Modelo {model} cargado en Ollama.")
    except Exception:
        pass  # No es crítico, query_ollama manejará el error si falla


def query_ollama(prompt: str, model: str = "mistral:latest", temperature: float = 0.3) -> str:
    """
    Envía un prompt a Ollama y devuelve la respuesta.
    
    Args:
        prompt: Texto del prompt completo.
        model: Nombre del modelo en Ollama.
        temperature: Creatividad (0.0 = determinista, 1.0 = creativo).
    
    Returns:
        Texto de respuesta del modelo.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_ctx": 16384,
                }
            },
            timeout=300,
        )
        response.raise_for_status()
        data = response.json()
        prompt_tokens = data.get("prompt_eval_count", 0)
        response_tokens = data.get("eval_count", 0)
        total_tokens = prompt_tokens + response_tokens
        print(f"Tokens usados — prompt: {prompt_tokens} | respuesta: {response_tokens} | total: {total_tokens} / 16384 ({round(total_tokens/16384*100)}%)")
        return data["response"]

    except requests.ConnectionError:
        print("ERROR: Ollama no está corriendo. Ejecuta 'ollama serve' en otra terminal.")
        raise
    except requests.Timeout:
        print("ERROR: Ollama tardó demasiado en responder (timeout 300s).")
        raise