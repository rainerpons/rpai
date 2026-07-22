from dataclasses import dataclass
from pathlib import Path

@dataclass
class Document:
    """
    Represents an ingested text file and its associated project context.
    
    Contains the original file content and identifying metadata to support
    future indexing and retrieval operations.
    """
    relative_path: Path
    content: str
    metadata: dict
