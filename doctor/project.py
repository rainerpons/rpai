import yaml
from pathlib import Path
from doctor import ValidationResult, ValidationError, ValidationSuccess
from core.config import load_project_config

def validate_project(config_path: str | Path) -> ValidationResult:
    path = Path(config_path)
    
    if not path.exists():
        return ValidationError(message=f"Configuration file not found: {path}")
        
    try:
        data = load_project_config(path)
    except yaml.YAMLError as e:
        return ValidationError(message=f"Invalid YAML in configuration file:\n{e}")
    except ValueError as e:
        return ValidationError(message=str(e))
    except Exception as e:
        return ValidationError(message=f"Failed to read configuration file: {e}")
        
    if "local_repository" not in data:
        return ValidationError(message="Missing required field: 'local_repository'")
        
    local_repo = data["local_repository"]
    if not isinstance(local_repo, str):
        return ValidationError(message="'local_repository' must be a string")
        
    repo_path = Path(local_repo).expanduser().resolve()
    
    if not repo_path.exists():
        return ValidationError(message=f"Local repository path does not exist: {repo_path}")
        
    if not repo_path.is_dir():
        return ValidationError(message=f"Local repository path is not a directory: {repo_path}")
        
    return ValidationSuccess(message=f"Project configuration is valid.\nLocal repository: {repo_path}")
