"""Flashcard generation logic."""

from typing import Optional

from corpus_callosum.db import DatabaseBackend

from .config import FlashcardConfig


class FlashcardGenerator:
    """Generate flashcards from documents in a collection."""

    def __init__(self, config: FlashcardConfig, db: DatabaseBackend):
        """Initialize flashcard generator.

        Args:
            config: Flashcard configuration
            db: Database backend
        """
        self.config = config
        self.db = db

    def generate(
        self, collection: str, difficulty: str = "intermediate", count: Optional[int] = None
    ) -> list[dict[str, str]]:
        """Generate flashcards from collection.

        Args:
            collection: Collection name
            difficulty: Difficulty level
            count: Number of cards to generate (uses config default if None)

        Returns:
            List of flashcard dicts with 'front' and 'back' keys
        """
        if count is None:
            count = self.config.cards_per_topic

        # Get full collection name with prefix
        full_collection = f"{self.config.collection_prefix}_{collection}"

        # Check if collection exists
        if not self.db.collection_exists(full_collection):
            raise ValueError(f"Collection '{full_collection}' does not exist")

        # For now, return placeholder flashcards
        # In full implementation, this would:
        # 1. Query the database for relevant documents
        # 2. Use LLM to generate flashcards from the documents
        # 3. Format according to config.format

        flashcards = []
        for i in range(count):
            flashcards.append(
                {
                    "front": f"Question {i+1} ({difficulty})",
                    "back": f"Answer {i+1}",
                    "difficulty": difficulty,
                    "collection": collection,
                }
            )

        return flashcards

    def format_flashcards(self, flashcards: list[dict[str, str]]) -> str:
        """Format flashcards according to config format.

        Args:
            flashcards: List of flashcard dicts

        Returns:
            Formatted flashcards string
        """
        if self.config.format == "anki":
            return self._format_anki(flashcards)
        elif self.config.format == "quizlet":
            return self._format_quizlet(flashcards)
        else:  # plain
            return self._format_plain(flashcards)

    def _format_anki(self, flashcards: list[dict[str, str]]) -> str:
        """Format as Anki import format."""
        lines = []
        for card in flashcards:
            lines.append(f"{card['front']}\t{card['back']}")
        return "\n".join(lines)

    def _format_quizlet(self, flashcards: list[dict[str, str]]) -> str:
        """Format as Quizlet import format."""
        lines = []
        for card in flashcards:
            lines.append(f"{card['front']}\t{card['back']}")
        return "\n".join(lines)

    def _format_plain(self, flashcards: list[dict[str, str]]) -> str:
        """Format as plain text."""
        lines = []
        for i, card in enumerate(flashcards, 1):
            lines.append(f"Card {i}:")
            lines.append(f"Q: {card['front']}")
            lines.append(f"A: {card['back']}")
            lines.append("")
        return "\n".join(lines)
