from pathlib import Path
from doctor.project import validate_project

def test_valid_configuration(tmp_path):
    # Create a valid project directory and config
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"local_repository: {repo_dir}\n")
    
    result = validate_project(config_file)
    assert result.success is True
    assert "Project configuration is valid" in result.message

def test_missing_configuration_file(tmp_path):
    config_file = tmp_path / "nonexistent.yaml"
    result = validate_project(config_file)
    assert result.success is False
    assert "Configuration file not found" in result.message

def test_malformed_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("local_repository: [unclosed list\n")
    
    result = validate_project(config_file)
    assert result.success is False
    assert "Invalid YAML" in result.message

def test_missing_local_repository(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("some_other_field: value\n")
    
    result = validate_project(config_file)
    assert result.success is False
    assert "Missing required field: 'local_repository'" in result.message

def test_nonexistent_repository_path(tmp_path):
    config_file = tmp_path / "config.yaml"
    nonexistent_path = tmp_path / "does_not_exist"
    config_file.write_text(f"local_repository: {nonexistent_path}\n")
    
    result = validate_project(config_file)
    assert result.success is False
    assert "Local repository path does not exist" in result.message

def test_repository_path_is_not_directory(tmp_path):
    file_path = tmp_path / "some_file.txt"
    file_path.write_text("hello")
    
    config_file = tmp_path / "config.yaml"
    config_file.write_text(f"local_repository: {file_path}\n")
    
    result = validate_project(config_file)
    assert result.success is False
    assert "Local repository path is not a directory" in result.message
