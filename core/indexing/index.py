"""
Indexing orchestration for project context.
"""
from typing import List, Optional
from pathlib import Path

from llama_index.core import Document as LlamaDocument
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from core.ingestion.models import Document as RPAIDocument
from core.indexing.store import get_storage_context

def get_default_embedding() -> BaseEmbedding:
    """
    Returns the default embedding model for project context.
    Using Alibaba-NLP/gte-modernbert-base as per implementation plan.
    """
    return HuggingFaceEmbedding(model_name="Alibaba-NLP/gte-modernbert-base")

def index_documents(
    documents: List[RPAIDocument], 
    project_config: dict, 
    state_dir: Path = Path("state"),
    embed_model: Optional[BaseEmbedding] = None
) -> VectorStoreIndex:
    """
    Chunks and embeds the provided RPAI documents into the project's vector store.
    
    Applies replace-by-document semantics using the repository-relative path as the
    document identity.
    """
    storage_context = get_storage_context(project_config, state_dir=state_dir)
    vector_store = storage_context.vector_store
    
    if embed_model is None:
        embed_model = get_default_embedding()
        
    llama_docs = []
    for doc in documents:
        # Normalize relative path (Rule 3)
        posix_path = doc.relative_path.as_posix()
        
        # Document identity (Rule 5)
        doc_id = posix_path
        
        # Preserve metadata (Rule 4)
        metadata = doc.metadata.copy()
        metadata["relative_path"] = posix_path
        
        llama_doc = LlamaDocument(
            text=doc.content,
            doc_id=doc_id,
            metadata=metadata,
        )
        llama_docs.append(llama_doc)
        
    # Use LlamaIndex standard text chunker (Rule 6)
    node_parser = SentenceSplitter()
    nodes = node_parser.get_nodes_from_documents(llama_docs)
    
    # Initialize VectorStoreIndex (Rule 7, 8)
    # We initialize the index from the vector store so that we can insert nodes.
    # Note: We must also pass the embedding model so chunks can be embedded.
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model,
    )
    
    # Apply replace-by-document semantics (Rule 9)
    # LlamaIndex vector stores (including Chroma) use ref_doc_id to manage nodes tied to a document.
    # We delete existing nodes for these documents before insertion.
    for doc in llama_docs:
        try:
            # Delete existing chunks associated with this document identity
            index.delete_ref_doc(doc.doc_id, delete_from_docstore=False)
        except Exception:
            # Ignoring exceptions if the document doesn't exist yet
            pass
            
    # Insert new nodes
    index.insert_nodes(nodes)
    
    return index
