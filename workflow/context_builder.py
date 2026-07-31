from collections.abc import Sequence

from core.retrieval.models import RetrievalResult
from workflow.models import Context

def build_context(retrieved_results: Sequence[RetrievalResult]) -> Context:
    context_parts = []
    for r in retrieved_results:
        source = r.metadata.get("relative_path", "unknown")
        context_parts.append(f"Source: {source}\n{r.text}")
        
    return Context(content="\n\n".join(context_parts))
