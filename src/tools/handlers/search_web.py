"""Read-only web search tool."""

from __future__ import annotations

from typing import Union
from pathlib import Path

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_RESULTS = 10
DEFAULT_TIMEOUT_SECONDS = 30


class SearchWebHandler:
    """Searches the web for information."""

    TOOL_NAME = "search_web"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        max_results: int = DEFAULT_MAX_RESULTS,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        if not isinstance(max_results, int) or max_results <= 0:
            raise ValueError("max_results must be a positive integer")
        if not isinstance(timeout_seconds, int) or timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be a positive integer")

        self._max_results = max_results
        self._timeout_seconds = timeout_seconds
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Searches the web for information using a search engine. Returns "
                "structured results with titles, URLs, and snippets. Read-only."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["query"],
                "properties": {
                    "query": {"type": "string", "description": "The search query."},
                    "num_results": {"type": "integer", "default": 10, "description": "Maximum number of results to return."},
                    "language": {"type": "string", "description": "Language code for search results (e.g., 'en', 'es')."},
                    "region": {"type": "string", "description": "Region code for search results (e.g., 'us', 'uk')."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "num_results": {"type": "integer"},
                    "results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "url": {"type": "string"},
                                "snippet": {"type": "string"},
                                "position": {"type": "integer"},
                            },
                        },
                    },
                    "total_results": {"type": "integer"},
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "web", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        raw_query = request.arguments.get("query")
        if not isinstance(raw_query, str) or not raw_query.strip():
            return self._failure(request, "invalid_argument", "argument 'query' must be a non-empty string")

        num_results = request.arguments.get("num_results", self._max_results)
        if not isinstance(num_results, int) or isinstance(num_results, bool) or num_results <= 0:
            return self._failure(request, "invalid_argument", "argument 'num_results' must be a positive integer")
        num_results = min(num_results, self._max_results)

        language = request.arguments.get("language")
        if language is not None and (not isinstance(language, str) or not language.strip()):
            return self._failure(request, "invalid_argument", "argument 'language' must be a non-empty string or null")

        region = request.arguments.get("region")
        if region is not None and (not isinstance(region, str) or not region.strip()):
            return self._failure(request, "invalid_argument", "argument 'region' must be a non-empty string or null")

        try:
            results, total_results = self._perform_search(raw_query, num_results, language, region)
        except ImportError as exc:
            return self._failure(
                request,
                "dependency_missing",
                f"Web search requires a search library or API: {exc}",
            )
        except Exception as exc:
            return self._failure(request, "search_error", f"failed to perform web search: {exc}")

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "query": raw_query,
                "num_results": num_results,
                "results": results,
                "total_results": total_results,
            },
            invocation_id=request.invocation_id,
        )

    def _perform_search(self, query: str, num_results: int, language: str | None, region: str | None) -> tuple[list[dict], int]:
        """Perform web search using available method."""
        try:
            from googlesearch import search as google_search
            urls = list(google_search(
                query,
                num_results=num_results,
                lang=language,
                region=region,
            ))
            results = []
            for i, url in enumerate(urls, 1):
                results.append({
                    "title": url,
                    "url": url,
                    "snippet": "",
                    "position": i,
                })
            return results, len(results)
        except ImportError:
            pass

        try:
            import requests
            import json
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
            }
            if language:
                params["kl"] = language
            response = requests.get(url, params=params, timeout=self._timeout_seconds)
            response.raise_for_status()
            data = response.json()
            results = []
            for i, result in enumerate(data.get("Results", [])[:num_results], 1):
                results.append({
                    "title": result.get("Title", ""),
                    "url": result.get("FirstURL", ""),
                    "snippet": result.get("Text", ""),
                    "position": i,
                })
            return results, len(data.get("Results", []))
        except ImportError:
            pass

        raise ImportError("No web search library available. Install googlesearch-python or requests.")

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
