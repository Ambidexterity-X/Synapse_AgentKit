"""Chroma/vector memory read-write helper used across agents."""

from __future__ import annotations

from memory.vector_store import MemoryRecord, VectorStore
from models import ResearchChunk
from tools.embed_tool import EmbedTool


class ChromaTool:
    """Facade for writing and querying research chunks in shared memory."""

    def __init__(self, vector_store: VectorStore, embed_tool: EmbedTool) -> None:
        self.vector_store = vector_store
        self.embed_tool = embed_tool

    def add_chunk(self, chunk: ResearchChunk) -> None:
        """Adds a research chunk to shared memory."""
        embedding = self.embed_tool.embed_text(chunk.content)
        record = MemoryRecord(
            record_id=chunk.chunk_id,
            document=chunk.content,
            metadata={
                "title": chunk.title,
                "url": chunk.source_url,
                "published_at": chunk.published_at,
            },
            embedding=embedding,
        )
        self.vector_store.add(record)

    def query(self, query_text: str, n_results: int = 5) -> list[ResearchChunk]:
        """Queries related chunks from shared memory."""
        query_embedding = self.embed_tool.embed_text(query_text)
        records = self.vector_store.query(query_embedding=query_embedding, n_results=n_results)

        chunks: list[ResearchChunk] = []
        for record in records:
            chunks.append(
                ResearchChunk(
                    chunk_id=record.record_id,
                    title=str(record.metadata.get("title", "Untitled")),
                    content=record.document,
                    source_url=str(record.metadata.get("url", "")),
                    published_at=record.metadata.get("published_at"),
                )
            )
        return chunks
