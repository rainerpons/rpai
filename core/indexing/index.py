"""
Indexing orchestration for project context.
"""
from typing import List, Optional
from pathlib import Path

from llama_index.core import Document as LlamaDocument
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.embeddings import BaseEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import IngestionPipeline, DocstoreStrategy

from core.ingestion.models import Document as RPAIDocument
from core.indexing.store import get_storage_context, get_project_state_dir

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
):
    """
    Chunks and embeds the provided RPAI documents into the project's vector store
    using LlamaIndex's IngestionPipeline.
    
    Applies DocstoreStrategy.UPSERTS to replace changed documents and skip unchanged ones.
    """
    # 1. Resolve storage
    project_state_dir = get_project_state_dir(project_config, state_dir)
    storage_context = get_storage_context(project_config, state_dir=state_dir)
    
    # 2. Setup Embedding
    if embed_model is None:
        embed_model = get_default_embedding()
        
    # 3. Convert Documents
    llama_docs = []
    for doc in documents:
        posix_path = doc.relative_path.as_posix()
        
        metadata = doc.metadata.copy()
        metadata["relative_path"] = posix_path
        
        llama_doc = LlamaDocument(
            text=doc.content,
            doc_id=posix_path,  # Use repository-relative path as document identity
            metadata=metadata,
        )
        llama_docs.append(llama_doc)
        
    # 4. Configure Ingestion Pipeline
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(),
            embed_model,
        ],
        vector_store=storage_context.vector_store,
        docstore=storage_context.docstore,
        docstore_strategy=DocstoreStrategy.UPSERTS,
    )
    
    # 5. Run Pipeline
    pipeline.run(documents=llama_docs)
    
    # 6. Persist Docstore State
    # The pipeline automatically persists to the vector store via Chroma, but we must
    # manually persist the docstore to ensure change detection works across sessions.
    storage_context.docstore.persist(persist_path=str(project_state_dir / "docstore.json"))

