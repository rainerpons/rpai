"""
Project-isolated index storage management using Chroma.
"""

from pathlib import Path
import re
import hashlib
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore
from core.config import resolve_local_repository

def _get_safe_project_key(project_config: dict) -> str:
    """
    Derives a safe, deterministic directory name from the project configuration.
    Uses the local repository path to generate a unique hash, appending it to the
    repository name to ensure duplicate names at different paths remain isolated.
    """
    repo_path = resolve_local_repository(project_config)
    repo_name = repo_path.name
    
    # Generate deterministic hash from the absolute path
    path_hash = hashlib.md5(str(repo_path.resolve()).encode("utf-8")).hexdigest()[:8]
    
    # Lowercase, replace non-alphanumeric with hyphens, strip extra hyphens
    safe_name = re.sub(r'[^a-z0-9]+', '-', repo_name.lower()).strip('-')
    if not safe_name:
        safe_name = "project"
        
    return f"{safe_name}-{path_hash}"

def get_storage_context(project_config: dict, state_dir: Path = Path("state")) -> StorageContext:
    """
    Resolves the persistent Chroma location for the project, initializes Chroma,
    and returns a LlamaIndex StorageContext wrapping the Chroma vector store
    and SimpleDocumentStore for change tracking.
    """
    project_key = _get_safe_project_key(project_config)
    
    # Isolate projects by placing them in separate directories under state/
    project_state_dir = state_dir / "chroma" / project_key
    project_state_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize persistent Chroma client for this project
    chroma_client = chromadb.PersistentClient(path=str(project_state_dir))
    chroma_collection = chroma_client.get_or_create_collection("project_context")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Initialize Docstore for tracking unchanged/changed documents
    docstore_path = project_state_dir / "docstore.json"
    if docstore_path.exists():
        docstore = SimpleDocumentStore.from_persist_dir(persist_dir=str(project_state_dir))
    else:
        docstore = SimpleDocumentStore()
        
    # Create and return the storage context
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore
    )
    return storage_context

