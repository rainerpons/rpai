from pathlib import Path
from typing import List

from .models import Document
from .discovery import discover_files
from .reader import read_text_file

def ingest_local_repository(project_config: dict) -> List[Document]:
    """
    Ingest a local repository as defined in the project configuration.
    
    Args:
        project_config: The loaded project configuration dictionary.
        
    Returns:
        A list of Document objects representing the supported text files in the repository.
        
    Raises:
        KeyError: If "local_repository" is missing.
        TypeError: If "local_repository" is not a string.
        FileNotFoundError: If the resolved repository path does not exist.
        NotADirectoryError: If the resolved repository path is not a directory.
    """
    local_repo = project_config["local_repository"]
    if not isinstance(local_repo, str):
        raise TypeError(f"'local_repository' must be a string, got {type(local_repo).__name__}")
        
    repo_path = Path(local_repo).expanduser().resolve()
    
    if not repo_path.exists():
        raise FileNotFoundError(f"Local repository path does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Local repository path is not a directory: {repo_path}")
        
    documents = []
    
    for file_path in discover_files(repo_path):
        content = read_text_file(file_path)
        if content is not None:
            # Successfully read text file
            doc = Document(
                relative_path=file_path.relative_to(repo_path),
                content=content,
                metadata={"repository_path": str(repo_path)}
            )
            documents.append(doc)
            
    return documents
