"""PDF to Markdown converter."""

from __future__ import annotations

from pathlib import Path

from .base import BaseConverter


class PdfConverter(BaseConverter):
    """Convert PDF files to Markdown."""

    extensions = (".pdf",)

    def convert(self, source: Path) -> str:
        """
        Convert PDF file to markdown.

        Extracts text from each page and formats with page markers.
        """
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF conversion requires pypdf. Install with: pip install pypdf"
            ) from exc

        reader = PdfReader(str(source))
        pages: list[str] = []

        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            text = text.strip()
            if text:
                # Add page marker for multi-page documents
                if len(reader.pages) > 1:
                    pages.append(f"## Page {i}\n\n{text}")
                else:
                    pages.append(text)

        return "\n\n".join(pages)
