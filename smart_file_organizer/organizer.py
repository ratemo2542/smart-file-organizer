"""Plan and perform file moves; dry-run uses the same plan as live mode."""

from __future__ import annotations

import shutil
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple

from .categories import get_category


@dataclass(frozen=True)
class Move:
    """One planned move."""
    source: Path
    destination: Path
    category: str

    @property
    def was_renamed(self) -> bool:
        return self.source.name != self.destination.name


@dataclass
class Summary:
    """Outcome of execute_moves()."""
    dry_run: bool
    moved: List[Move] = field(default_factory=list)
    failed: List[Tuple[Move, str]] = field(default_factory=list)

    def counts_by_category(self) -> Dict[str, int]:
        return dict(Counter(move.category for move in self.moved))


def unique_destination(destination: Path, reserved: Set[str]) -> Path:
    """Choose a free destination without overwriting existing files."""
    candidate = destination
    counter = 1
    while candidate.exists() or str(candidate).lower() in reserved:
        candidate = destination.with_name(
            f"{destination.stem} ({counter}){destination.suffix}"
        )
        counter += 1
    return candidate


def plan_moves(files: List[Path], root: Path) -> List[Move]:
    """Plan all moves without touching the filesystem."""
    moves: List[Move] = []
    reserved: Set[str] = set()
    for file_path in files:
        category = get_category(file_path)
        wanted = root / category / file_path.name
        destination = unique_destination(wanted, reserved)
        reserved.add(str(destination).lower())
        moves.append(Move(file_path, destination, category))
    return moves


def execute_moves(moves: List[Move], dry_run: bool = False) -> Summary:
    """Execute planned moves, or report them without filesystem changes."""
    summary = Summary(dry_run=dry_run)
    for move in moves:
        if dry_run:
            summary.moved.append(move)
            continue
        try:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.source), str(move.destination))
            summary.moved.append(move)
        except OSError as exc:
            summary.failed.append((move, exc.strerror or str(exc)))
    return summary
