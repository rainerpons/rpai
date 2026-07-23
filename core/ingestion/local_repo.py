from pathlib import Path
from typing import List

from core.config import resolve_local_repository
from .models import Document
from .discovery import discover_files
from .reader import read_text_file

def ingest_local_repository(project_config: dict) -> List[Document]:
    """
    Ingest a local repository as defined in the project configuration.
    
    Discovers supported files in the configured local repository and 
    returns them as a sequence of Document objects.
    """
    repo_path = resolve_local_repository(project_config)
    
    ingestion_config = project_config.get("ingestion", {})
    include_ignored = ingestion_config.get("include_ignored", [])
    
    documents = []
    
    for file_path in discover_files(repo_path, include_ignored):
        content = read_text_file(file_path)
        if content is not None:
            doc = Document(
                relative_path=file_path.relative_to(repo_path),
                content=content,
                metadata={"repository_path": str(repo_path)}
            )
            documents.append(doc)
            
    return documents
