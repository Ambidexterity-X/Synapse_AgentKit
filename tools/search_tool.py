"""Web search tool using Tavily with an offline fallback mode."""

from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from typing import Any

try:
    requests = importlib.import_module("requests")
except ImportError:
    requests = None


@dataclass(slots=True)
class SearchResult:
    """Single web search result used by the Researcher agent."""

    title: str
    content: str
    url: str
    published_date: str | None = None


class TavilySearchTool:
    """Tavily API wrapper with deterministic local fallback data."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Searches the web for relevant documents."""
        if self.api_key and requests is not None:
            try:
                request_exception = getattr(requests, "RequestException", RuntimeError)
                payload: dict[str, Any] = {
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "search_depth": "advanced",
                }
                response = requests.post(
                    "https://api.tavily.com/search",
                    json=payload,
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                return [
                    SearchResult(
                        title=item.get("title", "Untitled"),
                        content=item.get("content", ""),
                        url=item.get("url", ""),
                        published_date=item.get("published_date"),
                    )
                    for item in results[:max_results]
                ]
            except (request_exception, ValueError, KeyError, TypeError):
                pass

        return self._offline_results(query, max_results)

    @staticmethod
    def _offline_results(query: str, max_results: int) -> list[SearchResult]:
        base_content = (
            "Offline fallback result. Configure TAVILY_API_KEY for live web research. "
            f"Topic focus: {query}."
        )
        results = []
        for idx in range(max_results):
            results.append(
                SearchResult(
                    title=f"Local research note {idx + 1}",
                    content=base_content,
                    url=f"local://research/{idx + 1}",
                    published_date=None,
                )
            )
        return results
