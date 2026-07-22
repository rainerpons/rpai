import pytest
from pathlib import Path
from core.ingestion.discovery import discover_files
from core.ingestion.reader import read_text_file
from core.ingestion.local_repo import ingest_local_repository

FIXTURE_DIR = Path("tests/fixtures/sample_repo").resolve()

def test_discover_files():
    discovered = list(discover_files(FIXTURE_DIR))
    
    expected = [
        FIXTURE_DIR / "invalid.bin",
        FIXTURE_DIR / "nested" / "nested.txt",
        FIXTURE_DIR / "root.txt"
    ]
    
    assert discovered == expected

def test_read_text_file_success():
    path = FIXTURE_DIR / "root.txt"
    content = read_text_file(path)
    assert content.strip() == "root content"

def test_read_text_file_invalid_utf8():
    path = FIXTURE_DIR / "invalid.bin"
    content = read_text_file(path)
    assert content is None

def test_read_text_file_io_error(tmp_path):
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
    project_config = {"local_repository": str(FIXTURE_DIR)}
    documents = ingest_local_repository(project_config)
    
    assert len(documents) == 2
    
    assert documents[0].relative_path == Path("nested/nested.txt")
    assert documents[0].content.strip() == "nested content"
    assert documents[0].metadata["repository_path"] == str(FIXTURE_DIR)
    assert isinstance(documents[0].metadata["repository_path"], str)
    
    assert documents[1].relative_path == Path("root.txt")
    assert documents[1].content.strip() == "root content"
    assert documents[1].metadata["repository_path"] == str(FIXTURE_DIR)
    assert isinstance(documents[1].metadata["repository_path"], str)

def test_ingest_local_repository_determinism():
    project_config = {"local_repository": str(FIXTURE_DIR)}
    run1 = ingest_local_repository(project_config)
    run2 = ingest_local_repository(project_config)
    
    assert [d.relative_path for d in run1] == [d.relative_path for d in run2]
    assert [d.content for d in run1] == [d.content for d in run2]
