from typing import Optional, List
from pathlib import Path

from llama_index.core.embeddings import BaseEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore

from core.indexing.store import get_storage_context
from core.indexing.index import get_default_embedding

def retrieve_context(
    query: str,
    project_config: dict,
    top_k: int = 5,
    state_dir: Path = Path("state"),
    embed_model: Optional[BaseEmbedding] = None,
) -> List[NodeWithScore]:
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
    return retriever.retrieve(query)
