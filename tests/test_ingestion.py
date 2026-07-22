import pytest
from pathlib import Path
from core.ingestion.discovery import discover_files
from core.ingestion.reader import read_text_file
from core.ingestion.local_repo import ingest_local_repository

FIXTURE_DIR = Path("tests/fixtures/sample_repo").resolve()

def test_discover_files():
    """
    Verifies that discover_files yields candidate file paths in a deterministic, 
    lexicographical order while explicitly excluding standard metadata directories.
    """
    discovered = list(discover_files(FIXTURE_DIR))
    
    expected = [
        FIXTURE_DIR / "invalid.bin",
        FIXTURE_DIR / "nested" / "nested.txt",
        FIXTURE_DIR / "root.txt"
    ]
    
    assert discovered == expected
    
    # Explicitly prove exclusions worked
    discovered_names = [p.name for p in discovered]
    assert "config" not in discovered_names  # .git/config is excluded
    assert "cached.pyc" not in discovered_names  # __pycache__/cached.pyc is excluded

def test_read_text_file_success():
    """Verifies successful UTF-8 decoding of a supported text file."""
    path = FIXTURE_DIR / "root.txt"
    content = read_text_file(path)
    assert content == "root content\n"

def test_read_text_file_invalid_utf8():
    """Verifies that decoding errors signify an unsupported file, returning None."""
    path = FIXTURE_DIR / "invalid.bin"
    content = read_text_file(path)
    assert content is None

def test_read_text_file_io_error(tmp_path):
    """Verifies that unrelated I/O errors are propagated."""
    path = tmp_path / "does_not_exist.txt"
    with pytest.raises(FileNotFoundError):
        read_text_file(path)

def test_ingest_local_repository_missing_key():
    with pytest.raises(KeyError):
        ingest_local_repository({"other_key": "value"})

def test_ingest_local_repository_non_string_key():
    with pytest.raises(TypeError):
        ingest_local_repository({"local_repository": 123})

def test_ingest_local_repository_nonexistent(tmp_path):
    with pytest.raises(FileNotFoundError):
        ingest_local_repository({"local_repository": str(tmp_path / "missing")})

def test_ingest_local_repository_not_directory(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")
    with pytest.raises(NotADirectoryError):
        ingest_local_repository({"local_repository": str(file_path)})

def test_ingest_local_repository_success():
    """
    Verifies that ingestion properly orchestrates discovery and reading, 
    omits unsupported files, and correctly formats Document objects.
    """
    project_config = {"local_repository": str(FIXTURE_DIR)}
    documents = ingest_local_repository(project_config)
    
    assert len(documents) == 2
    
    # Ensure binary/unsupported files are absent
    ingested_paths = [doc.relative_path for doc in documents]
    assert Path("invalid.bin") not in ingested_paths
    
    # Assert exact Document values
    assert documents[0].relative_path == Path("nested/nested.txt")
    assert documents[0].content == "nested content\n"
    assert documents[0].metadata["repository_path"] == str(FIXTURE_DIR)
    
    assert documents[1].relative_path == Path("root.txt")
    assert documents[1].content == "root content\n"
    assert documents[1].metadata["repository_path"] == str(FIXTURE_DIR)
