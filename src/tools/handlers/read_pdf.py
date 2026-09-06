"""Read-only PDF text extraction tool confined to a shared workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_FILE_SIZE_BYTES = 10_485_760  # 10 MiB


class ReadPdfHandler:
    """Extracts text content from a PDF file within the tool's configured workspace."""

    TOOL_NAME = "read_pdf"

    def __init__(
        self,
        base_dir: Union[str, Path],
        *,
        max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    ) -> None:
        self._workspace = Workspace(base_dir)
        self._base_dir = self._workspace.base_dir
        if not isinstance(max_file_size_bytes, int) or max_file_size_bytes <= 0:
            raise ValueError("max_file_size_bytes must be a positive integer")

        self._max_file_size_bytes = max_file_size_bytes
        self._definition = ToolDefinition(
            name=self.TOOL_NAME,
            description=(
                "Extracts text content from a PDF file within the tool's configured "
                "workspace directory. Read-only. Requires PyPDF2 or pypdf library."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string", "description": "Path to the PDF file relative to the workspace."},
                    "page_numbers": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific page numbers to extract (1-indexed). Extracts all pages if not provided.",
                    },
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "num_pages": {"type": "integer"},
                    "text": {"type": "string"},
                    "size_bytes": {"type": "integer"},
                },
            },
            risk_level=RiskLevel.LOW,
            requires_confirmation=False,
            metadata={"category": "document", "read_only": True},
        )

    def definition(self) -> ToolDefinition:
        return self._definition

    def execute(self, request: ToolRequest) -> ToolResult:
        raw_path = request.arguments.get("path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            return self._failure(request, "invalid_argument", "argument 'path' must be a non-empty string")

        try:
            candidate = self._workspace.resolve_path(raw_path)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        if not candidate.exists():
            return self._failure(request, "file_not_found", f"no such file: {raw_path}")
        if not candidate.is_file():
            return self._failure(request, "not_a_file", f"path is not a regular file: {raw_path}")

        try:
            size_bytes = candidate.stat().st_size
        except OSError as exc:
            code, message = self._workspace.runtime_error(exc)
            return self._failure(request, code, message)

        if size_bytes > self._max_file_size_bytes:
            return self._failure(
                request,
                "file_too_large",
                f"file is {size_bytes} bytes, exceeds the {self._max_file_size_bytes} byte limit for this tool",
            )

        page_numbers = request.arguments.get("page_numbers")
        if page_numbers is not None:
            if not isinstance(page_numbers, list):
                return self._failure(request, "invalid_argument", "argument 'page_numbers' must be a list")
            for item in page_numbers:
                if not isinstance(item, int) or isinstance(item, bool):
                    return self._failure(request, "invalid_argument", "all items in 'page_numbers' must be integers")
            page_numbers = [int(p) for p in page_numbers]

        try:
            text, num_pages = self._extract_text(candidate, page_numbers)
        except ImportError as exc:
            return self._failure(
                request,
                "dependency_missing",
                f"PDF extraction requires PyPDF2 or pypdf library: {exc}",
            )
        except Exception as exc:
            return self._failure(request, "extraction_error", f"failed to extract PDF text: {exc}")

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": self._workspace.relative_path(candidate),
                "num_pages": num_pages,
                "text": text,
                "size_bytes": size_bytes,
            },
            invocation_id=request.invocation_id,
        )

    def _extract_text(self, path: Path, page_numbers: list[int] | None) -> tuple[str, int]:
        """Extract text from PDF using available library."""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
        except ImportError:
            try:
                from pypdf import PdfReader
                reader = PdfReader(path)
            except ImportError:
                raise ImportError("Neither PyPDF2 nor pypdf is installed")

        num_pages = len(reader.pages)
        text_parts = []

        if page_numbers:
            pages_to_extract = [p - 1 for p in page_numbers if 1 <= p <= num_pages]  # Convert to 0-indexed
        else:
            pages_to_extract = range(num_pages)

        for page_idx in pages_to_extract:
            page = reader.pages[page_idx]
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        return "\n\n---\n\n".join(text_parts), num_pages

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
