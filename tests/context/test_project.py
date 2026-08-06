import pytest
from pathlib import Path
from unittest.mock import patch

from context.indexing.project import build_project_index
from context.ingestion.models import Document

@patch("context.indexing.project.index_documents")
@patch("context.indexing.project.ingest_local_repository")
def test_build_project_index(mock_ingest, mock_index):
    project_config = {"name": "test"}
    state_dir = Path("/tmp/state")
    
    mock_docs = [Document(Path("f.txt"), "C", {})]
    mock_ingest.return_value = mock_docs
    
    build_project_index(project_config, state_dir=state_dir)
    
    mock_ingest.assert_called_once_with(project_config)
    mock_index.assert_called_once_with(mock_docs, project_config, state_dir=state_dir)

@patch("context.indexing.project.index_documents")
@patch("context.indexing.project.ingest_local_repository")
def test_build_project_index_propagates_ingestion_error(mock_ingest, mock_index):
    mock_ingest.side_effect = RuntimeError("Ingestion failed")
    
    with pytest.raises(RuntimeError, match="Ingestion failed"):
        build_project_index({"name": "test"})
        
    mock_index.assert_not_called()

@patch("context.indexing.project.index_documents")
@patch("context.indexing.project.ingest_local_repository")
def test_build_project_index_propagates_indexing_error(mock_ingest, mock_index):
    mock_index.side_effect = RuntimeError("Indexing failed")
    
    with pytest.raises(RuntimeError, match="Indexing failed"):
        build_project_index({"name": "test"})
