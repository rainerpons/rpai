from dataclasses import dataclass
from pathlib import Path

@dataclass
class Document:
    """
    Represents an ingested text file and its associated project context.
    """
    relative_path: Path
    content: str
    metadata: dict
