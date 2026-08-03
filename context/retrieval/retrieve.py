
from pathlib import Path

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core import VectorStoreIndex

from context.indexing.store import get_storage_context
from context.embeddings import get_default_embedding
from context.retrieval.models import RetrievalResult

def retrieve_context(
    query: str,
    project_config: dict,
    top_k: int = 5,
    state_dir: Path = Path("state"),
    embed_model: BaseEmbedding | None = None,
) -> list[RetrievalResult]:
    """
    Retrieve semantic context for a query from a project's index.
    """
    if not query or not query.strip():
        raise ValueError("query must contain non-whitespace text")
    
    if top_k <= 0:
        raise ValueError("top_k must be > 0")

    storage_context = get_storage_context(project_config, state_dir=state_dir)
    
    if embed_model is None:
        embed_model = get_default_embedding()

    index = VectorStoreIndex.from_vector_store(
        vector_store=storage_context.vector_store,
        embed_model=embed_model,
    )
    
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes_with_score = retriever.retrieve(query)
    
    return [
        RetrievalResult(
            text=node_with_score.node.text,
            metadata=node_with_score.node.metadata.copy(),
            score=node_with_score.score
        )
        for node_with_score in nodes_with_score
    ]
