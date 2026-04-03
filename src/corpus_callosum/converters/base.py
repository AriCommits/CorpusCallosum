"""Base classes for file format converters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ConversionResult:
    """Result of a single file conversion."""

    source_path: Path
    output_path: Path | None
    success: bool
    error: str | None = None


class BaseConverter(ABC):
    """Abstract base class for file format converters."""

    # Subclasses must define supported extensions, e.g., (".pdf",)
    extensions: tuple[str, ...] = ()

    @abstractmethod
    def convert(self, source: Path) -> str:
        """
        Convert file content to markdown string.

        Args:
            source: Path to the source file

        Returns:
            Markdown-formatted string

        Raises:
            Exception: If conversion fails
        """

    def can_convert(self, path: Path) -> bool:
        """Check if this converter can handle the given file."""
        return path.suffix.lower() in self.extensions
