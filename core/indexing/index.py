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
    return HuggingFaceEmbedding(model_name="Alibaba-NLP/gte-modernbert-base")

def index_documents(
    documents: List[RPAIDocument], 
    project_config: dict, 
    state_dir: Path = Path("state"),
    embed_model: Optional[BaseEmbedding] = None
):
    project_state_dir = get_project_state_dir(project_config, state_dir)
    storage_context = get_storage_context(project_config, state_dir=state_dir)
    
    if embed_model is None:
        embed_model = get_default_embedding()
        
    llama_docs = []
    for doc in documents:
        posix_path = doc.relative_path.as_posix()
        
        metadata = doc.metadata.copy()
        metadata["relative_path"] = posix_path
        
        llama_doc = LlamaDocument(
            text=doc.content,
            doc_id=posix_path,
            metadata=metadata,
        )
        llama_docs.append(llama_doc)
        
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(),
            embed_model,
        ],
        vector_store=storage_context.vector_store,
        docstore=storage_context.docstore,
        # LlamaIndex owns document change detection. Unchanged documents are skipped,
        # and changed documents replace their previous indexed representation entirely.
        docstore_strategy=DocstoreStrategy.UPSERTS,
    )
    
    # Bound each pipeline run so generated chunks stay within Chroma's insertion limits.
    batch_size = 100
    for i in range(0, len(llama_docs), batch_size):
        batch = llama_docs[i : i + batch_size]
        pipeline.run(documents=batch, store_doc_text=False)
    
    # Chroma persists the vector data automatically, but the docstore must be 
    # separately persisted to preserve the document hashes and state needed 
    # for LlamaIndex to recognize unchanged and changed documents across runs.
    storage_context.docstore.persist(persist_path=str(project_state_dir / "docstore.json"))
