"""Sequential orchestration for the multi-agent content pipeline."""

from __future__ import annotations

import os

from agents.editor import EditorAgent
from agents.publisher import PublisherAgent
from agents.researcher import ResearcherAgent
from agents.seo_optimizer import SeoOptimizerAgent
from agents.writer import WriterAgent
from memory.vector_store import VectorStore
from models import PipelineResult
from tools.chroma_tool import ChromaTool
from tools.embed_tool import EmbedTool
from tools.llm_tool import OllamaTool
from tools.search_tool import TavilySearchTool


class ContentPipeline:
    """Coordinates five agents in sequence to generate final content."""

    def __init__(self, output_dir: str = "output") -> None:
        use_openvino = os.getenv("USE_OPENVINO", "0").strip() == "1"
        embed_tool = EmbedTool(prefer_openvino=use_openvino)
        vector_store = VectorStore(collection_name="research")
        chroma_tool = ChromaTool(vector_store=vector_store, embed_tool=embed_tool)
        search_tool = TavilySearchTool()
        llm_tool = OllamaTool(model="mistral")

        self.researcher = ResearcherAgent(search_tool=search_tool, chroma_tool=chroma_tool)
        self.writer = WriterAgent(chroma_tool=chroma_tool, llm_tool=llm_tool)
        self.editor = EditorAgent(chroma_tool=chroma_tool, llm_tool=llm_tool)
        self.seo = SeoOptimizerAgent(embed_tool=embed_tool)
        self.publisher = PublisherAgent(output_dir=output_dir)

    def run(self, topic: str, destination: str = "markdown") -> PipelineResult:
        """Runs the full multi-agent pipeline for a single topic."""
        brief = self.researcher.run(topic=topic)
        draft = self.writer.run(brief=brief)
        polished = self.editor.run(draft=draft)
        seo_article, metadata = self.seo.run(article=polished)
        return self.publisher.run(article=seo_article, metadata=metadata, destination=destination)
