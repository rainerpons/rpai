import pytest
from pathlib import Path
from core.ingestion.discovery import discover_files
from core.ingestion.reader import read_text_file
from core.ingestion.local_repo import ingest_local_repository

def test_discover_files_no_gitignore(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    (repo_dir / "valid.txt").write_text("content")
    (repo_dir / "nested").mkdir()
    (repo_dir / "nested" / "nested.txt").write_text("content")
    
    (repo_dir / ".git").mkdir()
    (repo_dir / ".git" / "config").write_text("git config")
    
    discovered = list(discover_files(repo_dir))
    
    assert discovered == [
        repo_dir / "nested" / "nested.txt",
        repo_dir / "valid.txt"
    ]

def test_discover_files_gitignore(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    (repo_dir / ".gitignore").write_text(".venv/\nignore_me.txt\n")
    (repo_dir / "valid.txt").write_text("content")
    (repo_dir / "ignore_me.txt").write_text("ignore")
    
    (repo_dir / ".venv").mkdir()
    (repo_dir / ".venv" / "junk.txt").write_text("junk")
    
    discovered = list(discover_files(repo_dir))
    
    assert discovered == [
        repo_dir / ".gitignore",
        repo_dir / "valid.txt"
    ]

def test_discover_files_include_ignored(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    (repo_dir / ".gitignore").write_text("docs/\n.venv/\n")
    (repo_dir / "valid.txt").write_text("content")
    
    (repo_dir / "docs").mkdir()
    (repo_dir / "docs" / "doc.txt").write_text("doc")
    (repo_dir / "docs" / "nested").mkdir()
    (repo_dir / "docs" / "nested" / "nested_doc.txt").write_text("doc")
    
    (repo_dir / ".venv").mkdir()
    (repo_dir / ".venv" / "junk.txt").write_text("junk")
    
    include_ignored = ["docs/**"]
    
    discovered = list(discover_files(repo_dir, include_ignored))
    
    assert discovered == [
        repo_dir / ".gitignore",
        repo_dir / "docs" / "doc.txt",
        repo_dir / "docs" / "nested" / "nested_doc.txt",
        repo_dir / "valid.txt"
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
    
    (repo_dir / ".gitignore").write_text("ignored/\n")
    (repo_dir / "ignored").mkdir()
    (repo_dir / "ignored" / "file.txt").write_text("hello\n")
    (repo_dir / "ignored" / "included.txt").write_text("included\n")
    
    (repo_dir / "root.txt").write_text("root content\n")
    (repo_dir / "invalid.bin").write_bytes(b"\xff\xfe\xfd")
    
    config = {
        "local_repository": str(repo_dir),
        "ingestion": {
            "include_ignored": ["ignored/included.txt"]
        }
    }
    
    documents = ingest_local_repository(config)
    
    ingested_paths = [doc.relative_path for doc in documents]
    assert ingested_paths == [
        Path(".gitignore"),
        Path("ignored/included.txt"),
        Path("root.txt")
    ]
    
    assert documents[0].content == "ignored/\n"
    assert documents[1].content == "included\n"
    assert documents[2].content == "root content\n"
