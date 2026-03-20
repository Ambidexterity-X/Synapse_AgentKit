"""Editor agent implementation."""

from __future__ import annotations

from models import DraftArticle
from tools.chroma_tool import ChromaTool
from tools.llm_tool import OllamaTool


class EditorAgent:
    """Improves clarity and removes unsupported claims."""

    def __init__(self, chroma_tool: ChromaTool, llm_tool: OllamaTool) -> None:
        self.chroma_tool = chroma_tool
        self.llm_tool = llm_tool

    def run(self, draft: DraftArticle) -> DraftArticle:
        """Polishes markdown and performs lightweight fact checks."""
        support_chunks = self.chroma_tool.query(draft.topic, n_results=5)
        support_text = "\n\n".join(chunk.content for chunk in support_chunks)

        system_prompt = (
            "You are an expert editor. Improve structure and clarity, remove unsupported claims, "
            "and return polished markdown only."
        )
        user_prompt = (
            "Draft:\n"
            f"{draft.markdown}\n\n"
            "Supporting notes:\n"
            f"{support_text}"
        )

        polished = self.llm_tool.generate(system_prompt=system_prompt, user_prompt=user_prompt)
        return DraftArticle(topic=draft.topic, markdown=polished)
