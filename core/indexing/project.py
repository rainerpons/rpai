from pathlib import Path

from core.ingestion.local_repo import ingest_local_repository
from core.indexing.index import index_documents

def build_project_index(
    project_config: dict,
    *,
    state_dir: Path = Path("state"),
) -> None:
    # Ingest the repository using the config
    documents = ingest_local_repository(project_config)
    
    # Pass resulting documents to index_documents
    index_documents(documents, project_config, state_dir=state_dir)
