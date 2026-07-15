import yaml
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ValidationResult:
    success: bool
    message: str | None = None

def validate_project(config_path: str | Path) -> ValidationResult:
    path = Path(config_path)
    
    if not path.exists():
        return ValidationResult(success=False, message=f"Configuration file not found: {path}")
        
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return ValidationResult(success=False, message=f"Invalid YAML in configuration file:\n{e}")
    except Exception as e:
        return ValidationResult(success=False, message=f"Failed to read configuration file: {e}")
        
    if not isinstance(data, dict):
        return ValidationResult(success=False, message="Configuration file must contain a YAML object/dictionary")
        
    if "local_repository" not in data:
        return ValidationResult(success=False, message="Missing required field: 'local_repository'")
        
    local_repo = data["local_repository"]
    if not isinstance(local_repo, str):
        return ValidationResult(success=False, message="'local_repository' must be a string")
        
    repo_path = Path(local_repo).expanduser().resolve()
    
    if not repo_path.exists():
        return ValidationResult(success=False, message=f"Local repository path does not exist: {repo_path}")
        
    if not repo_path.is_dir():
        return ValidationResult(success=False, message=f"Local repository path is not a directory: {repo_path}")
        
    return ValidationResult(success=True, message=f"Project configuration is valid.\nLocal repository: {repo_path}")
