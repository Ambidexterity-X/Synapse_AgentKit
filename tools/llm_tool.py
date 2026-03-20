"""LLM helper for calling Ollama with a safe local fallback."""

from __future__ import annotations

import importlib
from typing import Any

try:
    ollama_module = importlib.import_module("ollama")
    Client = getattr(ollama_module, "Client")
except (ImportError, AttributeError):
    Client = None


class OllamaTool:
    """Provides chat generation through Ollama if available."""

    def __init__(self, model: str = "mistral", host: str = "http://localhost:11434") -> None:
        self.model = model
        self.host = host
        self._client = Client(host=host) if Client is not None else None

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generates text from prompts."""
        if self._client is not None:
            try:
                response: Any = self._client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return str(response["message"]["content"]).strip()
            except (OSError, RuntimeError, ValueError, KeyError, TypeError):
                pass

        return self._fallback_response(user_prompt)

    @staticmethod
    def _fallback_response(user_prompt: str) -> str:
        snippet = user_prompt[:1200].strip()
        return (
            "# Draft\n\n"
            "Ollama is unavailable, so this fallback draft was generated locally.\n\n"
            f"Input summary:\n\n{snippet}\n"
        )
