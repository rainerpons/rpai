import yaml
from pathlib import Path

def load_project_config(path: str | Path) -> dict:
    """
    Load and parse a project configuration YAML file.
    
    Validates that the file contains a top-level dictionary object.
    Propagates underlying filesystem or YAML parsing exceptions.
    """
    path = Path(path)
    
    with path.open('r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a YAML object/dictionary")
        
    return data

def resolve_local_repository(project_config: dict) -> Path:
    """
    Extract and resolve the local repository path from a project configuration.
    
    Validates the presence, type, and existence of the configured repository path.
    """
    if "local_repository" not in project_config:
        raise ValueError("Missing required field: 'local_repository'")
        
    local_repo = project_config["local_repository"]
    if not isinstance(local_repo, str):
        raise TypeError("'local_repository' must be a string")
        
    repo_path = Path(local_repo).expanduser().resolve()
    
    if not repo_path.exists():
        raise FileNotFoundError(f"Local repository path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Local repository path is not a directory: {repo_path}")
        
    return repo_path
