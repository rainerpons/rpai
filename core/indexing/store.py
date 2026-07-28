"""
Project-isolated index storage management using Chroma.
"""

from pathlib import Path
import re
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext

def _get_safe_project_key(project_config: dict) -> str:
    """
    Derives a safe, deterministic directory name from the project configuration.
    Falls back to 'default' if no name or canonical source is identifiable, though
    a name should generally be present.
    """
    if "name" in project_config and project_config["name"]:
        name = project_config["name"]
    elif "github_repository" in project_config and project_config["github_repository"]:
        name = project_config["github_repository"]
    else:
        name = "default"
        
    # Lowercase, replace non-alphanumeric with hyphens, strip extra hyphens
    safe_name = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return safe_name or "default"

def get_storage_context(project_config: dict, state_dir: Path = Path("state")) -> StorageContext:
    """
    Resolves the persistent Chroma location for the project, initializes Chroma,
    and returns a LlamaIndex StorageContext wrapping the Chroma vector store.
    """
    project_key = _get_safe_project_key(project_config)
    
    # Isolate projects by placing them in separate chroma databases/directories under state/chroma/
    chroma_db_dir = state_dir / "chroma" / project_key
    chroma_db_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize persistent Chroma client for this project
    chroma_client = chromadb.PersistentClient(path=str(chroma_db_dir))
    
    # Use a default collection name for the project since the db is already isolated
    chroma_collection = chroma_client.get_or_create_collection("project_context")
    
    # Wrap in LlamaIndex vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    # Create and return the storage context
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context
