"""Command-line interface for Smart File Organizer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from . import __version__
from .categories import all_category_names
from .organizer import Move, Summary, execute_moves, plan_moves
from .scanner import DirectoryError, scan_directory, validate_directory

EXIT_OK = 0
EXIT_PARTIAL_FAILURE = 1
EXIT_BAD_DIRECTORY = 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smart-file-organizer",
        description="Organize files into category folders by extension.",
        epilog="Tip: always preview first with --dry-run.",
    )
    parser.add_argument("directory", nargs="?", default=".",
                        help="folder to organize (default: current folder)")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="show what would happen without moving files")
    parser.add_argument("-a", "--include-hidden", action="store_true",
                        help="also organize hidden files")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print only the summary")
    parser.add_argument("-v", "--version", action="version",
                        version=f"%(prog)s {__version__}")
    return parser


def format_move(move: Move, root: Path) -> str:
    target = move.destination.relative_to(root).as_posix()
    note = "   (renamed: name already taken)" if move.was_renamed else ""
    return f"  {move.source.name}  ->  {target}{note}"


def print_summary(summary: Summary) -> None:
    verb = "would be moved" if summary.dry_run else "moved"
    counts = summary.counts_by_category()
    print("\nSummary")
    print("-------")
    for category in all_category_names():
        if category in counts:
            print(f"  {category:<12}{counts[category]:>4}")
    print(f"  {'Total':<12}{len(summary.moved):>4}  file(s) {verb}")
    if summary.failed:
        print(f"\n{len(summary.failed)} file(s) could not be moved:")
        for move, reason in summary.failed:
            print(f"  {move.source.name}: {reason}")


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = validate_directory(args.directory)
        files = scan_directory(root, include_hidden=args.include_hidden)
    except DirectoryError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return EXIT_BAD_DIRECTORY

    print(f"Smart File Organizer v{__version__}")
    print(f"Directory: {root}")
    print("Mode: DRY RUN (no files will be moved)" if args.dry_run
          else "Mode: LIVE (files will be moved)")
    if not files:
        print("\nNothing to organize: no files found in this folder.")
        return EXIT_OK

    moves = plan_moves(files, root)
    try:
        summary = execute_moves(moves, dry_run=args.dry_run)
    except KeyboardInterrupt:
        print("\nInterrupted. Files already moved stay where they are.",
              file=sys.stderr)
        return EXIT_PARTIAL_FAILURE

    if not args.quiet:
        print()
        for move in summary.moved:
            print(format_move(move, root))
    print_summary(summary)
    return EXIT_PARTIAL_FAILURE if summary.failed else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
