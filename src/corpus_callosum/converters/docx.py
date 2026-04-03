"""DOCX to Markdown converter."""

from __future__ import annotations

from pathlib import Path

from .base import BaseConverter


class DocxConverter(BaseConverter):
    """Convert Microsoft Word DOCX files to Markdown."""

    extensions = (".docx",)

    def convert(self, source: Path) -> str:
        """
        Convert DOCX file to markdown.

        Preserves headings and paragraph structure.
        """
        try:
            from docx import Document
        except ImportError as exc:
            raise RuntimeError(
                "DOCX conversion requires python-docx. Install with: pip install python-docx"
            ) from exc

        doc = Document(str(source))
        lines: list[str] = []

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Check for heading styles
            style_name = para.style.name if para.style else ""

            if style_name.startswith("Heading"):
                # Extract heading level (Heading 1, Heading 2, etc.)
                level = 1
                if style_name[-1].isdigit():
                    level = int(style_name[-1])
                level = min(level, 6)  # Markdown supports h1-h6
                lines.append(f"{'#' * level} {text}")
            elif style_name == "Title":
                lines.append(f"# {text}")
            elif style_name == "Subtitle":
                lines.append(f"## {text}")
            else:
                lines.append(text)

        return "\n\n".join(lines)
