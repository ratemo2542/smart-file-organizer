"""Decide which category a file belongs to, based on its extension.

This module is pure data + one lookup function. It knows nothing about
folders, moving files, or the terminal, which makes it very easy to test.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Set, Union

CATEGORIES: Dict[str, Set[str]] = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
               ".svg", ".tiff", ".heic", ".ico"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md",
                  ".xls", ".xlsx", ".csv", ".ppt", ".pptx"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv",
               ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
}
DEFAULT_CATEGORY = "Others"
_EXTENSION_TO_CATEGORY: Dict[str, str] = {
    ext: category for category, extensions in CATEGORIES.items()
    for ext in extensions
}


def get_category(file_path: Union[str, Path]) -> str:
    """Return category; extension matching is case-insensitive."""
    extension = Path(file_path).suffix.lower()
    return _EXTENSION_TO_CATEGORY.get(extension, DEFAULT_CATEGORY)


def all_category_names() -> List[str]:
    """Return every category name, including the default one."""
    return [*CATEGORIES, DEFAULT_CATEGORY]
