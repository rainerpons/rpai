from dataclasses import dataclass
from pathlib import Path

@dataclass
class Document:
    relative_path: Path
    content: str
    metadata: dict
