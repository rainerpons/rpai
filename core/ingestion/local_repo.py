from pathlib import Path
from typing import List

from .models import Document
from .discovery import discover_files
from .reader import read_text_file

def ingest_local_repository(project_config: dict) -> List[Document]:
    """
    Ingest a local repository as defined in the project configuration.
    
    Discovers supported files in the configured local repository and 
    returns them as a sequence of Document objects.
    """
    # Extract and validate the ingestion boundary
    local_repo = project_config["local_repository"]
    if not isinstance(local_repo, str):
        raise TypeError(f"'local_repository' must be a string, got {type(local_repo).__name__}")
        
    repo_path = Path(local_repo).expanduser().resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"Local repository path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Local repository path is not a directory: {repo_path}")
        
    documents = []
    
    # Process files in deterministic order
    for file_path in discover_files(repo_path):
        content = read_text_file(file_path)
        if content is not None:
            doc = Document(
                relative_path=file_path.relative_to(repo_path),
                content=content,
                metadata={"repository_path": str(repo_path)}
            )
            documents.append(doc)
            
    return documents
