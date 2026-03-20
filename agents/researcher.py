"""Researcher agent implementation."""

from __future__ import annotations

from models import ResearchBrief, ResearchChunk
from tools.search_tool import TavilySearchTool
from tools.chroma_tool import ChromaTool


class ResearcherAgent:
    """Finds sources, summarizes content, and stores chunks in memory."""

    def __init__(self, search_tool: TavilySearchTool, chroma_tool: ChromaTool) -> None:
        self.search_tool = search_tool
        self.chroma_tool = chroma_tool

    def run(self, topic: str, max_results: int = 5) -> ResearchBrief:
        """Runs research and returns a brief for downstream agents."""
        results = self.search_tool.search(query=topic, max_results=max_results)
        chunks: list[ResearchChunk] = []

        for idx, result in enumerate(results):
            chunk = ResearchChunk(
                chunk_id=f"doc_{idx + 1:03d}",
                title=result.title,
                content=result.content,
                source_url=result.url,
                published_at=result.published_date,
            )
            self.chroma_tool.add_chunk(chunk)
            chunks.append(chunk)

        return ResearchBrief(topic=topic, chunks=chunks)
