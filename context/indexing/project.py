from pathlib import Path

from context.ingestion.local_repo import ingest_local_repository
from context.indexing.index import index_documents

def build_project_index(
    project_config: dict,
    *,
    state_dir: Path = Path("state"),
) -> None:
    documents = ingest_local_repository(project_config)
    index_documents(documents, project_config, state_dir=state_dir)
