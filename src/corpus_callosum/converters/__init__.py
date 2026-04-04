"""Converter registry and utilities."""

from __future__ import annotations

from .base import BaseConverter, ConversionResult
from .docx import DocxConverter
from .html import HtmlConverter
from .pdf import PdfConverter
from .rtf import RtfConverter
from .txt import TxtConverter

__all__ = [
    "BaseConverter",
    "ConversionResult",
    "DocxConverter",
    "HtmlConverter",
    "PdfConverter",
    "RtfConverter",
    "TxtConverter",
    "get_all_converters",
]


def get_all_converters() -> list[BaseConverter]:
    """Return instances of all available converters."""
    return [
        TxtConverter(),
        PdfConverter(),
        DocxConverter(),
        HtmlConverter(),
        RtfConverter(),
    ]
