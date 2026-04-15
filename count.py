import os
from pathlib import Path


def count_lines_in_file(file_path: Path) -> int:
    """Count lines in a single file."""
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0


def count_python_lines(root_dir: Path) -> tuple[int, int]:
    """
    Recursively find all .py files and count total lines.
    
    Returns:
        (file_count, total_lines)
    """
    total_lines = 0
    file_count = 0

    for path in root_dir.rglob("*.py"):
        if path.is_file():
            lines = count_lines_in_file(path)
            total_lines += lines
            file_count += 1

    return file_count, total_lines


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Count lines in all .py files recursively.")
    parser.add_argument("directory", nargs="?", default="/home/levinten/redsnake/git/redsnake/src/redsnake", help="Root directory (default: current directory)")
    args = parser.parse_args()

    root = Path(args.directory).resolve()

    if not root.exists():
        print(f"Directory does not exist: {root}")
        exit(1)

    file_count, total_lines = count_python_lines(root)

    print(f"Scanned directory: {root}")
    print(f"Python files found: {file_count}")
    print(f"Total lines: {total_lines}")