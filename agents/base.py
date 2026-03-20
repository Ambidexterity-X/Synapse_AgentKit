"""Base protocol for all pipeline agents."""

from __future__ import annotations

from dataclasses import dataclass

from tools.chroma_tool import ChromaTool
from tools.embed_tool import EmbedTool
from tools.llm_tool import OllamaTool
from tools.search_tool import TavilySearchTool


@dataclass(slots=True)
class AgentDependencies:
    """Dependency bundle shared by all agents."""

    search_tool: TavilySearchTool
    chroma_tool: ChromaTool
    embed_tool: EmbedTool
    llm_tool: OllamaTool
