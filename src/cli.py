"""Unified cross-platform CLI entry point for CorpusRAG."""

from pathlib import Path

import click

from cli_dev import dev
from db.management import db
from orchestrations.cli import orchestrate
from tools.flashcards.cli import flashcards
from tools.quizzes.cli import quizzes
from tools.rag.cli import rag
from tools.summaries.cli import summaries
from tools.video.cli import video


@click.group()
@click.version_option(package_name="corpusrag")
def corpus() -> None:
    """CorpusRAG — unified learning and knowledge management toolkit.

    Run any subcommand with --help for details.
    """


@corpus.command()
@click.option("--reset", is_flag=True, help="Reset setup and re-run wizard")
def setup(reset: bool) -> None:
    """Run interactive setup wizard for first-time configuration."""
    marker_file = Path(".corpus_setup_complete")

    # Check if setup has already been completed
    if marker_file.exists() and not reset:
        click.echo(
            "Setup already completed. Use --reset to run wizard again or "
            "'corpus rag ui' to start using CorpusRAG."
        )
        return

    # Remove marker if resetting
    if reset and marker_file.exists():
        marker_file.unlink()
        click.echo("Resetting setup...")

    # Import and run setup wizard
    from setup_wizard import run_setup_wizard

    exit_code = run_setup_wizard()
    if exit_code != 0:
        raise click.ClickException("Setup wizard failed")


corpus.add_command(rag)
corpus.add_command(video)
corpus.add_command(orchestrate)
corpus.add_command(flashcards)
corpus.add_command(summaries)
corpus.add_command(quizzes)
corpus.add_command(db)
corpus.add_command(dev)


def main() -> None:
    """Entry point for the unified corpus CLI."""
    corpus()


if __name__ == "__main__":
    main()
