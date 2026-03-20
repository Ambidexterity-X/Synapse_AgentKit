"""Shared vector memory backed by ChromaDB with a lightweight fallback."""

from __future__ import annotations

from dataclasses import dataclass
import importlib
from math import sqrt
from typing import Any

try:
    chromadb = importlib.import_module("chromadb")
except ImportError:
    chromadb = None


@dataclass(slots=True)
class MemoryRecord:
    """A single record persisted in shared memory."""

    record_id: str
    document: str
    metadata: dict[str, Any]
    embedding: list[float]


class VectorStore:
    """In-memory vector store with optional ChromaDB acceleration."""

    def __init__(self, collection_name: str = "research") -> None:
        self.collection_name = collection_name
        self._fallback_records: list[MemoryRecord] = []
        self._collection = None

        if chromadb is not None:
            client = chromadb.Client()
            self._collection = client.get_or_create_collection(collection_name)

    def add(self, record: MemoryRecord) -> None:
        """Adds a single record to the configured vector store."""
        if self._collection is not None:
            self._collection.add(
                ids=[record.record_id],
                documents=[record.document],
                metadatas=[record.metadata],
                embeddings=[record.embedding],
            )
            return

        self._fallback_records.append(record)

    def query(self, query_embedding: list[float], n_results: int = 5) -> list[MemoryRecord]:
        """Queries the vector store and returns the nearest records."""
        if self._collection is not None:
            result = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )
            ids = result.get("ids", [[]])[0]
            documents = result.get("documents", [[]])[0]
            metadatas = result.get("metadatas", [[]])[0]
            embeddings = result.get("embeddings", [[]])[0]

            records: list[MemoryRecord] = []
            for idx, record_id in enumerate(ids):
                doc = documents[idx] if idx < len(documents) else ""
                meta = metadatas[idx] if idx < len(metadatas) else {}
                emb = embeddings[idx] if idx < len(embeddings) else []
                records.append(MemoryRecord(record_id, doc, meta or {}, emb or []))
            return records

        scored = [
            (self._cosine_similarity(query_embedding, record.embedding), record)
            for record in self._fallback_records
        ]
        scored.sort(key=lambda item: item[0], reverse=True)
        return [record for _, record in scored[:n_results]]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sqrt(sum(x * x for x in a))
        norm_b = sqrt(sum(y * y for y in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)
