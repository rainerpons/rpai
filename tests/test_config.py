import pytest
import yaml
from pathlib import Path
from core.config import load_project_config, resolve_local_repository

def test_load_project_config_success(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("local_repository: ~/foo\n")
    
    data = load_project_config(config_file)
    assert data == {"local_repository": "~/foo"}

def test_load_project_config_not_found(tmp_path):
    config_file = tmp_path / "missing.yaml"
    
    with pytest.raises(FileNotFoundError):
        load_project_config(config_file)

def test_load_project_config_invalid_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("unclosed: [list\n")
    
    with pytest.raises(yaml.YAMLError):
        load_project_config(config_file)

def test_load_project_config_not_dictionary(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("- just\n- a\n- list\n")
    
    with pytest.raises(ValueError) as exc:
        load_project_config(config_file)
    assert "Configuration file must contain a YAML object/dictionary" in str(exc.value)

def test_resolve_local_repository_missing_key():
    with pytest.raises(ValueError) as exc:
        resolve_local_repository({"other_key": "value"})
    assert "Missing required field: 'local_repository'" in str(exc.value)

def test_resolve_local_repository_non_string_key():
    with pytest.raises(TypeError) as exc:
        resolve_local_repository({"local_repository": 123})
    assert "'local_repository' must be a string" in str(exc.value)

def test_resolve_local_repository_nonexistent(tmp_path):
    missing_path = tmp_path / "missing"
    with pytest.raises(FileNotFoundError) as exc:
        resolve_local_repository({"local_repository": str(missing_path)})
    assert f"Local repository path does not exist: {missing_path}" in str(exc.value)

def test_resolve_local_repository_not_directory(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("hello")
    with pytest.raises(NotADirectoryError) as exc:
        resolve_local_repository({"local_repository": str(file_path)})
    assert f"Local repository path is not a directory: {file_path}" in str(exc.value)

def test_resolve_local_repository_success(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    resolved = resolve_local_repository({"local_repository": str(repo_dir)})
    assert resolved == repo_dir.resolve()
