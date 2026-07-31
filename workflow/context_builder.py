from collections.abc import Sequence

from core.retrieval.models import RetrievalResult
from workflow.context import Context, ContextEntry

def build_context(results: Sequence[RetrievalResult]) -> Context:
    entries = []
    for r in results:
        source = r.metadata.get("relative_path", "unknown")
        entries.append(ContextEntry(content=r.text, source=source))
        
    return Context(entries=tuple(entries))
