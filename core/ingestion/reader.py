from pathlib import Path
from typing import Optional

def read_text_file(file_path: Path) -> Optional[str]:
    """
    Read the contents of a supported text file.
    
    Returns None if the file content cannot be decoded as UTF-8,
    indicating it is unsupported. Other I/O errors are propagated.
    """
    try:
        with file_path.open('r', encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return None
