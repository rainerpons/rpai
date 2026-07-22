from pathlib import Path
from typing import Optional

def read_text_file(file_path: Path) -> Optional[str]:
    """
    Attempt to read a discovered file as UTF-8.
    
    Returns None if decoding raises UnicodeDecodeError, which defines
    unsupported files by behavior rather than extension.
    Allows other filesystem/I/O errors to propagate.
    """
    try:
        with file_path.open('r', encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return None
