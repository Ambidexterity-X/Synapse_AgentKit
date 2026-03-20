"""SEO optimizer agent implementation."""

from __future__ import annotations

from collections import Counter
import re

from models import DraftArticle, SeoMetadata
from tools.embed_tool import EmbedTool


class SeoOptimizerAgent:
    """Adds SEO metadata and heading guidance to article output."""

    def __init__(self, embed_tool: EmbedTool) -> None:
        self.embed_tool = embed_tool

    def run(self, article: DraftArticle, keyword_count: int = 8) -> tuple[DraftArticle, SeoMetadata]:
        """Computes SEO metadata and appends it to markdown."""
        _ = self.embed_tool.embed_text(article.markdown)

        tokens = self._extract_tokens(article.markdown)
        frequencies = Counter(tokens)
        top_keywords = [word for word, _ in frequencies.most_common(keyword_count)]

        total_tokens = max(len(tokens), 1)
        density = {
            keyword: round((frequencies[keyword] / total_tokens) * 100.0, 2)
            for keyword in top_keywords
        }

        title = f"{article.topic}: Complete Guide"
        description = (
            f"Learn about {article.topic} with practical insights, key trends, and implementation guidance."
        )
        headings = [
            f"# {article.topic}",
            "## Key Concepts",
            "## Practical Implementation",
            "## Challenges and Best Practices",
            "## Final Takeaways",
        ]

        metadata = SeoMetadata(
            seo_title=title,
            meta_description=description,
            target_keywords=top_keywords,
            heading_suggestions=headings,
            keyword_density=density,
        )

        metadata_block = self._render_metadata_block(metadata)
        updated_markdown = f"{article.markdown}\n\n{metadata_block}\n"
        return DraftArticle(topic=article.topic, markdown=updated_markdown), metadata

    @staticmethod
    def _extract_tokens(text: str) -> list[str]:
        return [token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text)]

    @staticmethod
    def _render_metadata_block(metadata: SeoMetadata) -> str:
        lines = [
            "---",
            "seo:",
            f"  title: \"{metadata.seo_title}\"",
            f"  meta_description: \"{metadata.meta_description}\"",
            f"  keywords: [{', '.join(metadata.target_keywords)}]",
            "  heading_suggestions:",
        ]
        lines.extend(f"    - {heading}" for heading in metadata.heading_suggestions)
        lines.append("  keyword_density_percent:")
        lines.extend(f"    {key}: {value}" for key, value in metadata.keyword_density.items())
        lines.append("---")
        return "\n".join(lines)
