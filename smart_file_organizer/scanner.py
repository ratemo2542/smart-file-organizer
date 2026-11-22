"""Find the files that should be organized.

This module only reads the filesystem. It never moves or changes anything.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Union


class DirectoryError(Exception):
    """Raised when the chosen directory is missing, invalid or unreadable."""


def validate_directory(path_text: Union[str, Path]) -> Path:
    """Turn user input into a safe, absolute directory path."""
    path = Path(path_text).expanduser()
    if not path.exists():
        raise DirectoryError(f"Path does not exist: {path}")
    if not path.is_dir():
        raise DirectoryError(f"Path is not a directory: {path}")
    return path.resolve()


def scan_directory(directory: Path, include_hidden: bool = False) -> List[Path]:
    """Return direct child files, sorted by name; skip folders and symlinks."""
    try:
        entries = list(directory.iterdir())
    except PermissionError as exc:
        raise DirectoryError(f"Permission denied: {directory}") from exc
    except OSError as exc:
        raise DirectoryError(f"Cannot read {directory}: {exc.strerror or exc}") from exc

    files = [
        entry for entry in entries
        if entry.is_file() and not entry.is_symlink()
        and (include_hidden or not entry.name.startswith("."))
    ]
    return sorted(files, key=lambda p: p.name.lower())
