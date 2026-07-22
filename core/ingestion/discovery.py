from pathlib import Path
from typing import Iterator

def discover_files(repo_path: Path) -> Iterator[Path]:
    """
    Recursively discover candidate files within a repository directory.
    
    Guarantees a deterministic traversal order and excludes standard
    repository metadata directories such as .git and __pycache__.
    """
    def _walk(directory: Path) -> Iterator[Path]:
        entries = sorted(directory.iterdir(), key=lambda p: p.relative_to(repo_path).as_posix())
        for entry in entries:
            if entry.is_dir():
                if entry.name not in {".git", "__pycache__"}:
                    yield from _walk(entry)
            else:
                yield entry

    yield from _walk(repo_path)
