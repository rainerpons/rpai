import pytest
import yaml
from pathlib import Path
from core.config import load_project_config

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
