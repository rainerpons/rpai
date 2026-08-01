from pathlib import Path

import core.retrieval
from workflow.context_builder import build_context
from workflow.language_model import LanguageModel
from workflow.models import WorkflowResult

def execute_task(
    task: str,
    project_config: dict,
    language_model: LanguageModel,
    *,
    top_k: int = 5,
    state_dir: Path = Path("state"),
) -> WorkflowResult:
    if not task or not task.strip():
        raise ValueError("Task must not be empty.")

    results = core.retrieval.retrieve_context(
        query=task,
        project_config=project_config,
        top_k=top_k,
        state_dir=state_dir,
    )
    
    context = build_context(results)

    output = language_model.generate(
        task=task,
        context=context,
    )

    return WorkflowResult(output=output)
