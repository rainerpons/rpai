import yaml
from pathlib import Path
from doctor import ValidationResult, ValidationError, ValidationSuccess

def validate_project(config_path: str | Path) -> ValidationResult:
    path = Path(config_path)
    
    if not path.exists():
        return ValidationError(message=f"Configuration file not found: {path}")
        
    try:
        with path.open('r', encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return ValidationError(message=f"Invalid YAML in configuration file:\n{e}")
    except Exception as e:
        return ValidationError(message=f"Failed to read configuration file: {e}")
        
    if not isinstance(data, dict):
        return ValidationError(message="Configuration file must contain a YAML object/dictionary")
        
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
