"""Cliente LLM que abstrae Ollama y permite fallback a APIs externas."""

import requests
import json


def query_ollama(prompt: str, model: str = "llama3.1:8b", temperature: float = 0.3) -> str:
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
                    "num_ctx": 8192,
                }
            },
            timeout=300,
        )
        response.raise_for_status()
        return response.json()["response"]

    except requests.ConnectionError:
        print("ERROR: Ollama no está corriendo. Ejecuta 'ollama serve' en otra terminal.")
        raise
    except requests.Timeout:
        print("ERROR: Ollama tardó demasiado en responder (timeout 300s).")
        raise