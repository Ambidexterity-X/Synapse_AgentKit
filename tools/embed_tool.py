"""Embedding generation tool with OpenVINO support and deterministic fallback."""

from __future__ import annotations

import hashlib
import importlib
import os
from typing import Sequence


class EmbedTool:
    """Generates embeddings using OpenVINO when available, else a hash embedding."""

    def __init__(
        self,
        model_name: str = "nomic-ai/nomic-embed-text-v1",
        device: str | None = None,
        dimensions: int = 384,
        prefer_openvino: bool | None = None,
    ) -> None:
        self.model_name = model_name
        self.device = device or os.getenv("EMBEDDING_DEVICE", "NPU")
        self.dimensions = dimensions
        if prefer_openvino is None:
            prefer_openvino = os.getenv("USE_OPENVINO", "0").strip() == "1"
        self.prefer_openvino = prefer_openvino
        self._tokenizer = None
        self._model = None
        self._ready = False
        if self.prefer_openvino:
            self._try_init_openvino()

    def embed_text(self, text: str) -> list[float]:
        """Embeds a single text string."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Embeds a batch of text strings."""
        if self._ready and self._tokenizer is not None and self._model is not None:
            tokens = self._tokenizer(
                list(texts),
                padding=True,
                truncation=True,
                return_tensors="pt",
            )
            outputs = self._model(**tokens)
            vectors = outputs.last_hidden_state.mean(dim=1).detach().cpu().numpy().tolist()
            return [self._normalize(vec) for vec in vectors]

        return [self._fallback_embed(text) for text in texts]

    def _try_init_openvino(self) -> None:
        try:
            optimum_intel = importlib.import_module("optimum.intel")
            transformers = importlib.import_module("transformers")

            self._tokenizer = transformers.AutoTokenizer.from_pretrained(self.model_name)
            self._model = optimum_intel.OVModelForFeatureExtraction.from_pretrained(
                self.model_name,
                export=False,
                device=self.device,
            )
            self._ready = True
        except (ImportError, AttributeError, OSError, RuntimeError, ValueError):
            self._ready = False

    def _fallback_embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = text.lower().split()
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[idx] += 1.0

        return self._normalize(vector)

    @staticmethod
    def _normalize(vector: Sequence[float]) -> list[float]:
        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0.0:
            return [float(value) for value in vector]
        return [float(value) / norm for value in vector]
