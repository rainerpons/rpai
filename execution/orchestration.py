from pathlib import Path

from execution.language_model import LanguageModel
from execution.models import WorkflowResult

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
    from execution.models import ContextItem

    retrieved_results = core.retrieval.retrieve_context(
        query=task,
        project_config=project_config,
        top_k=top_k,
        state_dir=state_dir,
    )
    
    context = [
        ContextItem(text=r.text, source=r.metadata.get("relative_path", "unknown")) 
        for r in retrieved_results
    ]

    generated_output = language_model.generate(
        task=task,
        context=context,
    )

    return WorkflowResult(output=generated_output)
