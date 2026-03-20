"""Writer agent implementation."""

from __future__ import annotations

from models import DraftArticle, ResearchBrief
from tools.chroma_tool import ChromaTool
from tools.llm_tool import OllamaTool


class WriterAgent:
    """Generates a long-form markdown article from research context."""

    def __init__(self, chroma_tool: ChromaTool, llm_tool: OllamaTool) -> None:
        self.chroma_tool = chroma_tool
        self.llm_tool = llm_tool

    def run(self, brief: ResearchBrief, n_context: int = 5) -> DraftArticle:
        """Generates the first markdown draft."""
        retrieved = self.chroma_tool.query(brief.topic, n_results=n_context)
        context_block = "\n\n".join(
            f"Title: {chunk.title}\nSource: {chunk.source_url}\nNotes: {chunk.content}"
            for chunk in retrieved
        )

        system_prompt = (
            "You are a professional long-form writer. Produce markdown with H2/H3 headings, "
            "an intro, body sections, and conclusion."
        )
        user_prompt = (
            f"Topic: {brief.topic}\n\n"
            "Use the context below to write a full article. Keep claims grounded in provided notes.\n\n"
            f"{context_block}"
        )

        markdown = self.llm_tool.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        return DraftArticle(topic=brief.topic, markdown=markdown)
