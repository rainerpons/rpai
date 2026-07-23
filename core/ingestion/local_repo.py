from pathlib import Path

from core.config import resolve_local_repository
from .models import Document
from .discovery import discover_files
from .reader import read_text_file

def ingest_local_repository(project_config: dict) -> list[Document]:
    """
    Ingest a local repository as defined in the project configuration.
    """
    repo_path = resolve_local_repository(project_config)
    include_ignored = project_config.get("ingestion", {}).get("include_ignored", [])
    
    documents = []
    for file_path in discover_files(repo_path, include_ignored):
        if (content := read_text_file(file_path)) is not None:
            documents.append(Document(
                relative_path=file_path.relative_to(repo_path),
                content=content,
                metadata={"repository_path": str(repo_path)}
            ))
            
    return documents
