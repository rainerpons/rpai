from pathlib import Path
from typing import Callable, Optional

import core.retrieval
from core.indexing import ensure_project_index, delete_project_index, build_project_index
from workflow.context_builder import build_context
from workflow.language_model import LanguageModel
from workflow.models import WorkflowResult

class ProjectIndexError(RuntimeError):
    pass

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

    for attempt in range(2):
        try:
            results = core.retrieval.retrieve_context(
                query=task,
                project_config=project_config,
                top_k=top_k,
                state_dir=state_dir,
            )
            break
        except Exception as error:
            if attempt == 1:
                raise ProjectIndexError(
                    "The project index could not be prepared. Run the command again after checking the project repository and local state permissions."
                ) from error
                
            cb("Existing project index could not be loaded. Rebuilding...")
            delete_project_index(project_config, state_dir=state_dir)
            build_project_index(project_config, state_dir=state_dir)
            cb("Project index rebuilt.")

    context = build_context(results)

    output = language_model.generate(
        task=task,
        context=context,
    )

    return WorkflowResult(output=output)
