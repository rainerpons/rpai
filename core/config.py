import yaml
from pathlib import Path

def load_project_config(path: str | Path) -> dict:
    """
    Load a project configuration YAML file.
    
    Args:
        path: Path to the YAML configuration file.
        
    Returns:
        The parsed dictionary from the YAML file.
        
    Raises:
        ValueError: If the parsed YAML is not a dictionary.
        Exception: Underlying file I/O exceptions or yaml.YAMLError propagate.
    """
    path = Path(path)
    
    with path.open('r', encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a YAML object/dictionary")
        
    return data
