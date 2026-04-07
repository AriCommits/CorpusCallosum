"""CLI commands for CorpusCallosum.

Provides simple command-line interfaces for common operations:
- corpus-ask: Query a collection
- corpus-flashcards: Generate flashcards from a collection
- corpus-collections: List all collections
- corpus-sync: Synchronize collections between backends
"""

from __future__ import annotations

import argparse
import asyncio
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
    parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        dest="top_k",
        help="Number of results to retrieve (default: from config)",
    )

    args = parser.parse_args()

    # Get question from positional arg or --query flag
    question = args.question or args.query_alt
    if not question:
        parser.error("Please provide a question as an argument or with -q/--query")

    # Validate top_k if provided
    if args.top_k is not None and args.top_k <= 0:
        parser.error("top_k must be a positive integer")

    agent = RagAgent()

    try:
        tokens, chunks = agent.query(
            query=question,
            collection_name=args.collection,
            model=args.model,
            session_id=args.session,
            top_k=args.top_k,
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


def sync_main() -> None:
    """CLI entry point for syncing collections."""
    parser = argparse.ArgumentParser(
        prog="corpus-sync",
        description="Synchronize collections between local and remote storage",
    )
    subparsers = parser.add_subparsers(dest="action", help="Sync action")

    # Common sync arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-c",
        "--collection",
        help="Collection name to sync (if not specified, uses --all)",
    )
    parent_parser.add_argument(
        "--all",
        action="store_true",
        help="Sync all collections",
    )
    parent_parser.add_argument(
        "--remote",
        help="Remote storage URL (not yet implemented)",
    )

    # Pull command
    pull_parser = subparsers.add_parser(
        "pull", help="Pull changes from remote to local", parents=[parent_parser]
    )
    pull_parser.add_argument(
        "--force",
        action="store_true",
        help="Force sync even if conflicts exist",
    )

    # Push command
    push_parser = subparsers.add_parser(
        "push", help="Push changes from local to remote", parents=[parent_parser]
    )
    push_parser.add_argument(
        "--force",
        action="store_true",
        help="Force sync even if conflicts exist",
    )

    # Bidirectional sync command
    sync_parser = subparsers.add_parser(
        "bidirectional", help="Sync in both directions", parents=[parent_parser]
    )
    sync_parser.add_argument(
        "--force",
        action="store_true",
        help="Force sync even if conflicts exist",
    )
    sync_parser.add_argument(
        "--strategy",
        choices=["last_write_wins", "manual_resolve", "keep_both"],
        default="last_write_wins",
        help="Conflict resolution strategy",
    )

    # Status command
    status_parser = subparsers.add_parser(
        "status", help="Show sync status", parents=[parent_parser]
    )

    # Diff command
    diff_parser = subparsers.add_parser(
        "diff", help="Show differences between local and remote", parents=[parent_parser]
    )

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        sys.exit(1)

    # Validate collection argument
    if not args.collection and not args.all:
        parser.error("Please specify --collection or --all")

    # Remote storage not yet implemented
    if args.remote:
        print("Error: Remote storage backends not yet implemented", file=sys.stderr)
        print("Currently only local ChromaDB storage is supported", file=sys.stderr)
        sys.exit(1)

    print("Sync functionality requires a configured remote backend.", file=sys.stderr)
    print("This feature is not yet fully implemented.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    # Allow running as module: python -m corpus_callosum.cli <command>
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        sys.argv = sys.argv[1:]  # Shift args
        if cmd == "ask":
            ask_main()
        elif cmd == "flashcards":
            flashcards_main()
        elif cmd == "collections":
            collections_main()
        elif cmd == "sync":
            sync_main()
        else:
            print(f"Unknown command: {cmd}")
            print("Available: ask, flashcards, collections, sync")
            sys.exit(1)
    else:
        print("Usage: python -m corpus_callosum.cli <command>")
        print("Available commands: ask, flashcards, collections, sync")
        sys.exit(1)
