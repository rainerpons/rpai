from pathlib import Path
from typing import Iterator

def discover_files(repo_path: Path) -> Iterator[Path]:
    """
    Recursively discover files within a repository.
    
    Yields candidate file Path objects in precise deterministic order:
    lexicographically sorted by path.relative_to(repo_path).as_posix().
    Explicitly excludes exactly `.git` and `__pycache__` directory names.
    Does not determine whether contents are text.
    """
    def _walk(directory: Path) -> Iterator[Path]:
        entries = sorted(directory.iterdir(), key=lambda p: p.relative_to(repo_path).as_posix())
        for entry in entries:
            if entry.is_dir():
                if entry.name not in {".git", "__pycache__"}:
                    yield from _walk(entry)
            else:
                yield entry

    if repo_path.is_dir():
        yield from _walk(repo_path)
