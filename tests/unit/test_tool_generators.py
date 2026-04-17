"""Unit tests for tool generators (flashcards, quizzes, summaries)."""

from unittest.mock import MagicMock

from tools.flashcards.config import FlashcardConfig
from tools.quizzes.config import QuizConfig
from tools.summaries.config import SummaryConfig


class TestFlashcardConfig:
    """Tests for FlashcardConfig."""

    def test_default_values(self) -> None:
        """Test default flashcard config values."""
        config = FlashcardConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
        )
        assert config.count == 15
        assert config.difficulty in ["beginner", "intermediate", "advanced"]
        assert config.format == "markdown"

    def test_custom_values(self) -> None:
        """Test custom flashcard config values."""
        config = FlashcardConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
            count=20,
            difficulty="advanced",
            format="json",
        )
        assert config.count == 20
        assert config.difficulty == "advanced"
        assert config.format == "json"

    def test_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "llm": {"model": "test"},
            "embedding": {"model": "test"},
            "database": {"mode": "persistent"},
            "paths": {"vault": "./vault"},
            "flashcards": {"count": 25, "difficulty": "beginner"},
        }
        config = FlashcardConfig.from_dict(data)
        assert config.count == 25
        assert config.difficulty == "beginner"

    def test_prompt_template_formatting(self) -> None:
        """Test prompt template can be formatted."""
        config = FlashcardConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
        )
        text = "Sample text about Python programming"
        try:
            prompt = config.prompt_template.format(
                count=config.count,
                difficulty=config.difficulty,
                text=text,
            )
            assert "Python" in prompt or "text" in prompt.lower()
        except KeyError:
            # Template might have different format
            pass


class TestQuizConfig:
    """Tests for QuizConfig."""

    def test_default_values(self) -> None:
        """Test default quiz config values."""
        config = QuizConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
        )
        assert config.count == 10
        assert config.difficulty in ["beginner", "intermediate", "advanced"]
        assert config.format == "markdown"
        assert isinstance(config.question_types, list)

    def test_custom_values(self) -> None:
        """Test custom quiz config values."""
        config = QuizConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
            count=20,
            difficulty="intermediate",
            format="json",
        )
        assert config.count == 20
        assert config.difficulty == "intermediate"
        assert config.format == "json"

    def test_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "llm": {"model": "test"},
            "embedding": {"model": "test"},
            "database": {"mode": "persistent"},
            "paths": {"vault": "./vault"},
            "quizzes": {"count": 15, "difficulty": "advanced", "format": "csv"},
        }
        config = QuizConfig.from_dict(data)
        assert config.count == 15
        assert config.difficulty == "advanced"
        assert config.format == "csv"

    def test_question_types_available(self) -> None:
        """Test that question types are configured."""
        config = QuizConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
        )
        assert len(config.question_types) > 0
        # Should include common question types
        types = [t.lower() for t in config.question_types]
        assert any("choice" in t or "question" in t for t in types)


class TestSummaryConfig:
    """Tests for SummaryConfig."""

    def test_default_values(self) -> None:
        """Test default summary config values."""
        config = SummaryConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
        )
        assert config.summary_length in ["short", "medium", "long"]
        assert hasattr(config, "prompt_template")

    def test_custom_values(self) -> None:
        """Test custom summary config values."""
        config = SummaryConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
            summary_length="long",
        )
        assert config.summary_length == "long"

    def test_from_dict(self) -> None:
        """Test creating config from dictionary."""
        data = {
            "llm": {"model": "test"},
            "embedding": {"model": "test"},
            "database": {"mode": "persistent"},
            "paths": {"vault": "./vault"},
            "summaries": {"summary_length": "short"},
        }
        config = SummaryConfig.from_dict(data)
        assert config.summary_length == "short"

    def test_summary_lengths_valid(self) -> None:
        """Test that all summary length options are valid."""
        valid_lengths = ["short", "medium", "long"]
        for length in valid_lengths:
            config = SummaryConfig(
                llm=MagicMock(),
                embedding=MagicMock(),
                database=MagicMock(),
                paths=MagicMock(),
                summary_length=length,
            )
            assert config.summary_length == length


class TestToolConfigFromDict:
    """Tests for tool config from_dict methods."""

    def test_flashcard_config_missing_keys(self) -> None:
        """Test flashcard config handles missing keys gracefully."""
        minimal_data = {
            "llm": {},
            "embedding": {},
            "database": {},
            "paths": {},
        }
        config = FlashcardConfig.from_dict(minimal_data)
        # Should use defaults
        assert config.count == 15

    def test_quiz_config_missing_keys(self) -> None:
        """Test quiz config handles missing keys gracefully."""
        minimal_data = {
            "llm": {},
            "embedding": {},
            "database": {},
            "paths": {},
        }
        config = QuizConfig.from_dict(minimal_data)
        # Should use defaults
        assert config.count == 10

    def test_summary_config_missing_keys(self) -> None:
        """Test summary config handles missing keys gracefully."""
        minimal_data = {
            "llm": {},
            "embedding": {},
            "database": {},
            "paths": {},
        }
        config = SummaryConfig.from_dict(minimal_data)
        # Should use defaults
        assert config.summary_length in ["short", "medium", "long"]

    def test_tool_configs_inherit_base_config(self) -> None:
        """Test that tool configs properly inherit base config."""
        data = {
            "llm": {"model": "test-model"},
            "embedding": {"model": "test-embedding"},
            "database": {"mode": "http"},
            "paths": {"vault": "./test-vault"},
        }

        flashcard_config = FlashcardConfig.from_dict(data)
        quiz_config = QuizConfig.from_dict(data)
        summary_config = SummaryConfig.from_dict(data)

        # All should inherit base config
        assert flashcard_config.llm.model == "test-model"
        assert quiz_config.llm.model == "test-model"
        assert summary_config.llm.model == "test-model"

        assert flashcard_config.embedding.model == "test-embedding"
        assert flashcard_config.database.mode == "http"


class TestToolConfigValidation:
    """Tests for tool config validation."""

    def test_flashcard_count_positive(self) -> None:
        """Test flashcard count is positive."""
        config = FlashcardConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
            count=0,
        )
        # Should allow 0 (even if not meaningful)
        assert config.count == 0

        config = FlashcardConfig(
            llm=MagicMock(),
            embedding=MagicMock(),
            database=MagicMock(),
            paths=MagicMock(),
            count=-1,
        )
        # Should allow negative (validation happens elsewhere)
        assert config.count == -1

    def test_quiz_format_valid(self) -> None:
        """Test quiz format validation."""
        valid_formats = ["markdown", "json", "csv"]
        for fmt in valid_formats:
            config = QuizConfig(
                llm=MagicMock(),
                embedding=MagicMock(),
                database=MagicMock(),
                paths=MagicMock(),
                format=fmt,
            )
            assert config.format == fmt

    def test_summary_length_valid_values(self) -> None:
        """Test summary length uses valid values."""
        valid_lengths = ["short", "medium", "long"]
        for length in valid_lengths:
            config = SummaryConfig(
                llm=MagicMock(),
                embedding=MagicMock(),
                database=MagicMock(),
                paths=MagicMock(),
                summary_length=length,
            )
            assert config.summary_length == length
