"""CLI commands for CorpusCallosum.

Provides simple command-line interfaces for common operations:
- corpus-ask: Query a collection
- corpus-flashcards: Generate flashcards from a collection
- corpus-collections: List all collections
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .agent import RagAgent
from .retriever import HybridRetriever


def ask_main() -> None:
    """CLI entry point for querying a collection."""
    parser = argparse.ArgumentParser(
        prog="corpus-ask",
        description="Ask a question against a document collection",
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="The question to ask",
    )
    parser.add_argument(
        "-q",
        "--query",
        dest="query_alt",
        help="Alternative way to specify the question",
    )
    parser.add_argument(
        "-c",
        "--collection",
        required=True,
        help="Collection name to query",
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Override the default model",
    )
    parser.add_argument(
        "-s",
        "--session",
        help="Session ID for multi-turn conversation",
    )

    args = parser.parse_args()

    # Get question from positional arg or --query flag
    question = args.question or args.query_alt
    if not question:
        parser.error("Please provide a question as an argument or with -q/--query")

    agent = RagAgent()

    try:
        tokens, chunks = agent.query(
            query=question,
            collection_name=args.collection,
            model=args.model,
            session_id=args.session,
        )

        # Print sources first
        if chunks:
            print(f"\n[Sources: {len(chunks)} chunks from '{args.collection}']\n")

        # Stream the response
        for token in tokens:
            print(token, end="", flush=True)
        print()  # Final newline

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def flashcards_main() -> None:
    """CLI entry point for generating flashcards."""
    parser = argparse.ArgumentParser(
        prog="corpus-flashcards",
        description="Generate study flashcards from a document collection",
    )
    parser.add_argument(
        "-c",
        "--collection",
        required=True,
        help="Collection name to generate flashcards from",
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Override the default model",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file (default: print to stdout)",
    )

    args = parser.parse_args()

    agent = RagAgent()

    try:
        tokens = agent.generate_flashcards(
            collection_name=args.collection,
            model=args.model,
        )

        output_lines: list[str] = []

        print(f"\nGenerating flashcards from '{args.collection}'...\n")

        # Collect and stream output
        for token in tokens:
            output_lines.append(token)
            print(token, end="", flush=True)
        print()  # Final newline

        # Write to file if requested
        if args.output:
            content = "".join(output_lines)
            Path(args.output).write_text(content, encoding="utf-8")
            print(f"\nFlashcards saved to: {args.output}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def collections_main() -> None:
    """CLI entry point for listing collections."""
    parser = argparse.ArgumentParser(
        prog="corpus-collections",
        description="List all document collections",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output as JSON",
    )

    args = parser.parse_args()

    retriever = HybridRetriever()

    try:
        collections = retriever.list_collections()

        if args.as_json:
            print(json.dumps({"collections": collections}, indent=2))
        elif collections:
            print("Collections:")
            for name in collections:
                print(f"  - {name}")
        else:
            print("No collections found.")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Allow running as module for testing
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        sys.argv = sys.argv[1:]  # Shift args
        if cmd == "ask":
            ask_main()
        elif cmd == "flashcards":
            flashcards_main()
        elif cmd == "collections":
            collections_main()
        else:
            print(f"Unknown command: {cmd}")
            print("Available: ask, flashcards, collections")
