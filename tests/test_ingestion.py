import pytest
from pathlib import Path
from core.ingestion.discovery import discover_files
from core.ingestion.reader import read_text_file
from core.ingestion.local_repo import ingest_local_repository

def test_discover_files(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    (repo_dir / "invalid.bin").write_bytes(b"\xff\xfe\xfd")
    
    nested = repo_dir / "nested"
    nested.mkdir()
    (nested / "nested.txt").write_text("nested content")
    
    (repo_dir / "root.txt").write_text("root content")
    
    dot_git = repo_dir / ".git"
    dot_git.mkdir()
    (dot_git / "config").write_text("git config")
    
    pycache = repo_dir / "__pycache__"
    pycache.mkdir()
    (pycache / "cached.pyc").write_text("compiled bytes")
    
    discovered = list(discover_files(repo_dir))
    
    assert discovered == [
        repo_dir / "invalid.bin",
        repo_dir / "nested" / "nested.txt",
        repo_dir / "root.txt"
    ]

def test_read_text_file_success(tmp_path):
    path = tmp_path / "root.txt"
    path.write_text("root content\n")
    
    content = read_text_file(path)
    assert content == "root content\n"

def test_read_text_file_invalid_utf8(tmp_path):
    path = tmp_path / "invalid.bin"
    path.write_bytes(b"\xff\xfe\xfd")
    
    content = read_text_file(path)
    assert content is None

def test_read_text_file_io_error(tmp_path):
    path = tmp_path / "missing.txt"
    
    with pytest.raises(FileNotFoundError):
        read_text_file(path)

def test_ingest_local_repository_success(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    nested = repo_dir / "nested"
    nested.mkdir()
    (nested / "nested.txt").write_text("nested content\n")
    
    (repo_dir / "root.txt").write_text("root content\n")
    (repo_dir / "invalid.bin").write_bytes(b"\xff\xfe\xfd")
    
    documents = ingest_local_repository({"local_repository": str(repo_dir)})
    
    ingested_paths = [doc.relative_path for doc in documents]
    assert ingested_paths == [
        Path("nested/nested.txt"),
        Path("root.txt")
    ]
    
    assert documents[0].content == "nested content\n"
    assert documents[0].metadata["repository_path"] == str(repo_dir)
    
    assert documents[1].content == "root content\n"
    assert documents[1].metadata["repository_path"] == str(repo_dir)
