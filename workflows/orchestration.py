from pathlib import Path

from workflows.language_model import LanguageModel
from workflows.models import WorkflowResult

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

    import core.retrieval

    context = core.retrieval.retrieve_context(
        query=task,
        project_config=project_config,
        top_k=top_k,
        state_dir=state_dir,
    )

    generated_output = language_model.generate(
        task=task,
        context=context,
    )

    return WorkflowResult(output=generated_output)
