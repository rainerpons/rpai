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
