from pathlib import Path
from typing import Iterator
import pathspec

def discover_files(repo_path: Path, include_ignored: list[str] | None = None) -> Iterator[Path]:
    """
    Recursively discover candidate files within a repository directory.
    
    Guarantees a deterministic traversal order and explicitly excludes .git.
    Respects .gitignore rules if present, while allowing specific patterns 
    to be explicitly re-included via include_ignored.
    """
    ignore_spec = None
    gitignore_path = repo_path / ".gitignore"
    if gitignore_path.is_file():
        with gitignore_path.open("r", encoding="utf-8") as f:
            ignore_spec = pathspec.PathSpec.from_lines("gitignore", f)
            
    include_spec = None
    if include_ignored:
        include_spec = pathspec.PathSpec.from_lines("gitignore", include_ignored)

    def _walk(directory: Path) -> Iterator[Path]:
        entries = sorted(directory.iterdir(), key=lambda p: p.relative_to(repo_path).as_posix())
        for entry in entries:
            if entry.name == ".git":
                continue
                
            if entry.is_dir():
                yield from _walk(entry)
            else:
                rel_path = entry.relative_to(repo_path).as_posix()
                
                is_ignored = ignore_spec.match_file(rel_path) if ignore_spec else False
                is_included = include_spec.match_file(rel_path) if include_spec else False
                
                if not is_ignored or is_included:
                    yield entry

    yield from _walk(repo_path)
