"""Summary generation logic."""

from typing import Optional

from corpus_callosum.db import DatabaseBackend

from .config import SummaryConfig


class SummaryGenerator:
    """Generate summaries from documents in a collection."""

    def __init__(self, config: SummaryConfig, db: DatabaseBackend):
        """Initialize summary generator.

        Args:
            config: Summary configuration
            db: Database backend
        """
        self.config = config
        self.db = db

    def generate(self, collection: str, topic: Optional[str] = None) -> dict[str, str]:
        """Generate summary from collection.

        Args:
            collection: Collection name
            topic: Optional specific topic to summarize

        Returns:
            Summary dict with 'summary', 'keywords', and 'outline' keys
        """
        # Get full collection name with prefix
        full_collection = f"{self.config.collection_prefix}_{collection}"

        # Check if collection exists
        if not self.db.collection_exists(full_collection):
            raise ValueError(f"Collection '{full_collection}' does not exist")

        # For now, return placeholder summary
        # In full implementation, this would:
        # 1. Query the database for relevant documents
        # 2. Use LLM to generate summary
        # 3. Extract keywords and create outline

        result = {
            "summary": f"Summary of {collection}" + (f" - {topic}" if topic else ""),
            "collection": collection,
        }

        if self.config.include_keywords:
            result["keywords"] = ["keyword1", "keyword2", "keyword3"]

        if self.config.include_outline:
            result["outline"] = [
                "I. Introduction",
                "II. Main Points",
                "III. Conclusion",
            ]

        return result

    def format_summary(self, summary: dict[str, str]) -> str:
        """Format summary as markdown.

        Args:
            summary: Summary dict

        Returns:
            Formatted summary string
        """
        lines = [f"# Summary: {summary['collection']}", ""]

        if "keywords" in summary and self.config.include_keywords:
            lines.append("## Keywords")
            lines.extend([f"- {kw}" for kw in summary["keywords"]])
            lines.append("")

        if "outline" in summary and self.config.include_outline:
            lines.append("## Outline")
            lines.extend(summary["outline"])
            lines.append("")

        lines.append("## Summary")
        lines.append(summary["summary"])

        return "\n".join(lines)
