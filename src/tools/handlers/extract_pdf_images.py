"""Read-only PDF image extraction tool confined to a shared workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from ..models import RiskLevel, ToolDefinition, ToolError, ToolRequest, ToolResult
from ..workspace import Workspace, WorkspacePathError

DEFAULT_MAX_FILE_SIZE_BYTES = 10_485_760  # 10 MiB


class ExtractPdfImagesHandler:
    """Extracts images from a PDF file within the tool's configured workspace."""

    TOOL_NAME = "extract_pdf_images"

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
                "Extracts images from a PDF file and saves them to a destination "
                "directory within the tool's configured workspace. Read-only. "
                "Requires pdf2image or PyMuPDF library."
            ),
            version="1.0.0",
            input_schema={
                "type": "object",
                "required": ["path"],
                "properties": {
                    "path": {"type": "string", "description": "Path to the PDF file relative to the workspace."},
                    "output_dir": {"type": "string", "description": "Directory to save extracted images. Defaults to 'pdf_images'."},
                    "dpi": {"type": "integer", "default": 200, "description": "DPI for extracted images."},
                },
            },
            output_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "output_dir": {"type": "string"},
                    "num_images": {"type": "integer"},
                    "images": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
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

        output_dir = request.arguments.get("output_dir", "pdf_images")
        if not isinstance(output_dir, str) or not output_dir.strip():
            return self._failure(request, "invalid_argument", "argument 'output_dir' must be a non-empty string")

        dpi = request.arguments.get("dpi", 200)
        if not isinstance(dpi, int) or isinstance(dpi, bool) or dpi <= 0:
            return self._failure(request, "invalid_argument", "argument 'dpi' must be a positive integer")

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

        try:
            output_path = self._workspace.resolve_path(output_dir)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        if not output_path.exists():
            try:
                output_path.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                code, message = self._workspace.runtime_error(exc)
                return self._failure(request, code, message)

        try:
            self._workspace.ensure_within(output_path, display_path=output_dir)
        except WorkspacePathError as exc:
            return self._failure(request, exc.code, exc.message)

        try:
            image_paths = self._extract_images(candidate, output_path, dpi)
        except ImportError as exc:
            return self._failure(
                request,
                "dependency_missing",
                f"PDF image extraction requires pdf2image or PyMuPDF library: {exc}",
            )
        except Exception as exc:
            return self._failure(request, "extraction_error", f"failed to extract PDF images: {exc}")

        relative_image_paths = [self._workspace.relative_path(p) for p in image_paths]

        return ToolResult(
            success=True,
            tool_name=self.TOOL_NAME,
            content={
                "path": self._workspace.relative_path(candidate),
                "output_dir": self._workspace.relative_path(output_path),
                "num_images": len(image_paths),
                "images": relative_image_paths,
                "size_bytes": size_bytes,
            },
            invocation_id=request.invocation_id,
        )

    def _extract_images(self, pdf_path: Path, output_dir: Path, dpi: int) -> list[Path]:
        """Extract images from PDF using available library."""
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(str(pdf_path), dpi=dpi)
            extracted_paths = []
            for i, image in enumerate(images):
                image_path = output_dir / f"page_{i+1}.png"
                image.save(str(image_path), "PNG")
                extracted_paths.append(image_path)
            return extracted_paths
        except ImportError:
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(str(pdf_path))
                extracted_paths = []
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    images = page.get_images(full=True)
                    for img_index, img in enumerate(images):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_path = output_dir / f"page_{page_num+1}_img_{img_index+1}.png"
                        with open(str(image_path), "wb") as f:
                            f.write(base_image["image"])
                        extracted_paths.append(image_path)
                return extracted_paths
            except ImportError:
                raise ImportError("Neither pdf2image nor PyMuPDF is installed")

    def _failure(self, request: ToolRequest, code: str, message: str) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.TOOL_NAME,
            error=ToolError(code=code, message=message),
            invocation_id=request.invocation_id,
        )
