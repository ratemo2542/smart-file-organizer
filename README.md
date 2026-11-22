# Smart File Organizer

A dependency-free Python CLI that tidies a folder (like `Downloads`) by moving files into category folders based on their extensions.

- Pure Python; standard library only
- Preview with `--dry-run` before moving anything
- Never overwrites existing files
- Clear summaries and friendly error messages

## Features

| Feature | Description |
|---|---|
| Categorization | Images, Documents, Videos, Audio, Archives, Others |
| Dry run | Preview actions without moving files |
| Collision protection | Existing names get safe numbered alternatives |
| Safe defaults | Skips subfolders, hidden files and symlinks |
| Case-insensitive | Handles uppercase and lowercase extensions |
| Error handling | Reports failures without stopping all processing |

## Requirements

Python 3.8 or newer. No third-party packages.

## Installation

```bash
git clone https://github.com/ratemo2542/smart-file-organizer.git
cd smart-file-organizer
python -m smart_file_organizer --help
```

Optional install:

```bash
pip install .
smart-file-organizer --help
```

## Usage

```bash
# Preview first (recommended)
python -m smart_file_organizer ~/Downloads --dry-run

# Organize for real
python -m smart_file_organizer ~/Downloads

# Organize current directory
python -m smart_file_organizer

# Show summary only
python -m smart_file_organizer ~/Downloads --quiet

# Include hidden files
python -m smart_file_organizer ~/Downloads --include-hidden
```

## Categories

| Folder | Extensions |
|---|---|
| Images | .jpg .jpeg .png .gif .bmp .webp .svg .tiff .heic .ico |
| Documents | .pdf .doc .docx .txt .rtf .odt .md .xls .xlsx .csv .ppt .pptx |
| Videos | .mp4 .mkv .avi .mov .wmv .flv .webm .m4v |
| Audio | .mp3 .wav .flac .aac .ogg .m4a .wma |
| Archives | .zip .rar .7z .tar .gz .bz2 .xz |
| Others | everything else |

## Project structure

```
smart-file-organizer/
├── smart_file_organizer/
│   ├── __init__.py
│   ├── __main__.py
│   ├── categories.py
│   ├── scanner.py
│   ├── organizer.py
│   └── cli.py
├── tests/
│   ├── test_categories.py
│   └── test_organizer.py
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
└── pyproject.toml
```

## How it works

1. Scan files directly inside the selected folder.
2. Categorize each file by extension.
3. Plan safe destinations and resolve name collisions.
4. Move files, or report planned moves in dry-run mode.
5. Print a summary.

## Tests

```bash
python -m unittest discover -v
```

## Safety

- Always try `--dry-run` first.
- Moves are not automatically undoable.
- Only files directly inside the selected folder are organized.

## License

MIT. See [LICENSE](LICENSE).
