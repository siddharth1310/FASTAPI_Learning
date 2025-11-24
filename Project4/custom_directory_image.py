from pathlib import Path

SKIP_DIRS = {".venv", "__pycache__", ".git", ".pytest_cache", "alembic", ".vscode"}
SKIP_FILE_EXTS = {".pyc", ".pyo", ".db"}
SKIP_FILES = {".DS_Store"}  # add more if needed


def dir_tree(root: Path, prefix: str = "") -> None:
    # Filter entries up front
    entries = [
        e for e in root.iterdir()
        if not (
            (e.is_dir() and e.name in SKIP_DIRS) or
            (e.is_file() and (e.suffix in SKIP_FILE_EXTS or e.name in SKIP_FILES))
        )
    ]
    entries = sorted(entries, key=lambda e: (e.is_file(), e.name.lower()))

    entries_count = len(entries)

    for idx, entry in enumerate(entries):
        connector = "└── " if idx == entries_count - 1 else "├── "
        print(prefix + connector + entry.name)

        if entry.is_dir():
            extension = "    " if idx == entries_count - 1 else "│   "
            dir_tree(entry, prefix + extension)


if __name__ == "__main__":
    dir_tree(Path("."))  # or Path("/path/to/your/project")
