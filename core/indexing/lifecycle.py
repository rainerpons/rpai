from pathlib import Path
from typing import Callable, Optional

from core.indexing.store import project_index_exists
from core.indexing.project import build_project_index

def ensure_project_index(
    project_config: dict,
    *,
    state_dir: Path = Path("state"),
    on_progress: Optional[Callable[[str], None]] = None,
) -> None:
    progress = on_progress or (lambda msg: None)

    if project_index_exists(project_config, state_dir=state_dir):
        return
        
    progress("Creating project index...")
    build_project_index(project_config, state_dir=state_dir)
    progress("Project index created.")
