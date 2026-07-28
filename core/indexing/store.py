import re
import hashlib
from pathlib import Path

import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.storage.docstore import SimpleDocumentStore

from core.config import resolve_local_repository

def _get_project_storage_key(project_config: dict) -> str:
    """
    Derives a deterministic, filesystem-safe directory name for a project.
    Duplicate repository names at different paths are isolated using a SHA-256 hash.
    """
    repo_path = resolve_local_repository(project_config)
    repo_name = repo_path.name
    
    path_hash = hashlib.sha256(str(repo_path.resolve()).encode("utf-8")).hexdigest()[:12]
    
    safe_name = re.sub(r'[^a-z0-9]+', '-', repo_name.lower()).strip('-')
    if not safe_name:
        safe_name = "project"
        
    return f"{safe_name}-{path_hash}"

def get_project_state_dir(project_config: dict, state_dir: Path = Path("state")) -> Path:
    project_key = _get_project_storage_key(project_config)
    return state_dir / "chroma" / project_key

def get_storage_context(project_config: dict, state_dir: Path = Path("state")) -> StorageContext:
    project_state_dir = get_project_state_dir(project_config, state_dir)
    project_state_dir.mkdir(parents=True, exist_ok=True)
    
    chroma_client = chromadb.PersistentClient(path=str(project_state_dir))
    chroma_collection = chroma_client.get_or_create_collection("project_context")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    docstore_path = project_state_dir / "docstore.json"
    if docstore_path.exists():
        docstore = SimpleDocumentStore.from_persist_path(str(docstore_path))
    else:
        docstore = SimpleDocumentStore()
        
    return StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore
    )

