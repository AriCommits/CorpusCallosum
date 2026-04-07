"""Plain text to Markdown converter."""

from __future__ import annotations

from pathlib import Path

from .base import BaseConverter


class TxtConverter(BaseConverter):
    """Convert plain text files to Markdown."""

    extensions = (".txt",)

    def convert(self, source: Path) -> str:
        """
        Convert text file to markdown.

        Plain text is already markdown-compatible, so this is mostly a passthrough.
        """
        text = source.read_text(encoding="utf-8", errors="ignore")
        return text.strip()
