from pathlib import Path
from typing import Callable, Optional

import context.retrieval
from context.indexing import ensure_project_index, delete_project_index, build_project_index, IndexLoadError
from orchestration.context_builder import build_context
from orchestration.language_model import LanguageModel
from orchestration.models import WorkflowResult

class ProjectIndexError(RuntimeError):
    pass

def _retrieve(task: str, project_config: dict, top_k: int, state_dir: Path) -> list:
    return context.retrieval.retrieve_context(
        query=task,
        project_config=project_config,
        top_k=top_k,
        state_dir=state_dir,
    )

def _recover_project_index(project_config: dict, state_dir: Path, cb: Callable[[str], None]) -> None:
    cb("Existing project index could not be loaded. Rebuilding...")
    delete_project_index(project_config, state_dir=state_dir)
    build_project_index(project_config, state_dir=state_dir)
    cb("Project index rebuilt.")

def _retrieve_with_recovery(
    task: str,
    project_config: dict,
    top_k: int,
    state_dir: Path,
    cb: Callable[[str], None],
) -> list:
    try:
        return _retrieve(task, project_config, top_k, state_dir)
    except IndexLoadError:
        _recover_project_index(project_config, state_dir, cb)
        
        try:
            return _retrieve(task, project_config, top_k, state_dir)
        except IndexLoadError as error:
            raise ProjectIndexError(
                "The project index could not be prepared. Run the command again after checking the project repository and local state permissions."
            ) from error

def execute_task(
    task: str,
    project_config: dict,
    language_model: LanguageModel,
    *,
    top_k: int = 5,
    state_dir: Path = Path("state"),
    progress: Optional[Callable[[str], None]] = None,
) -> WorkflowResult:
    if not task or not task.strip():
        raise ValueError("Task must not be empty.")

    cb = progress or (lambda msg: None)
    ensure_project_index(project_config, state_dir=state_dir, on_progress=progress)

    results = _retrieve_with_recovery(
        task=task,
        project_config=project_config,
        top_k=top_k,
        state_dir=state_dir,
        cb=cb,
    )

    context = build_context(results)

    output = language_model.generate(
        task=task,
        context=context,
    )

    return WorkflowResult(output=output)
