import yaml
from pathlib import Path
from doctor import ValidationResult, ValidationError, ValidationSuccess
from core.config import load_project_config, resolve_local_repository

def validate_project(config_path: str | Path) -> ValidationResult:
    path = Path(config_path)
    
    if not path.exists():
        return ValidationError(message=f"Configuration file not found: {path}")
        
    try:
        data = load_project_config(path)
        repo_path = resolve_local_repository(data)
    except yaml.YAMLError as e:
        return ValidationError(message=f"Invalid YAML in configuration file:\n{e}")
    except (ValueError, KeyError, TypeError, FileNotFoundError, NotADirectoryError) as e:
        return ValidationError(message=str(e))
    except Exception as e:
        return ValidationError(message=f"Failed to read configuration file: {e}")
        
    return ValidationSuccess(message=f"Project configuration is valid.\nLocal repository: {repo_path}")
