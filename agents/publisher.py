"""Publisher agent implementation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re

from models import DraftArticle, PipelineResult, SeoMetadata


class PublisherAgent:
    """Writes finalized article output and can be extended for API publishing."""

    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, article: DraftArticle, metadata: SeoMetadata, destination: str = "markdown") -> PipelineResult:
        """Publishes article to the selected destination."""
        if destination != "markdown":
            # Non-markdown destinations are placeholders for future API integrations.
            destination = "markdown"

        filename = self._build_filename(article.topic)
        output_path = self.output_dir / filename
        output_path.write_text(article.markdown, encoding="utf-8")

        return PipelineResult(
            topic=article.topic,
            output_path=str(output_path),
            markdown=article.markdown,
            metadata=metadata,
            created_at=datetime.utcnow(),
            extras={"destination": destination},
        )

    @staticmethod
    def _build_filename(topic: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
        if not slug:
            slug = "article"
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{slug}_{timestamp}.md"
