import pytest
import shutil
from pathlib import Path

from llama_index.core.embeddings import MockEmbedding
from llama_index.core import VectorStoreIndex

from core.ingestion.models import Document
from core.indexing.store import get_storage_context, _get_safe_project_key
from core.indexing.index import index_documents

@pytest.fixture
def mock_embed_model():
    # Use a small MockEmbedding for fast tests
    return MockEmbedding(embed_dim=10)

@pytest.fixture
def temp_state_dir(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    return state_dir

def test_safe_project_key(tmp_path):
    repo = tmp_path / "test-proj"
    repo.mkdir()
    assert "test-proj" in _get_safe_project_key({"name": "Test Project", "local_repository": str(repo)})

def test_index_ingested_documents(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "test-proj"
    repo.mkdir()
    project_config = {"name": "test-proj", "local_repository": str(repo)}
    
    docs = [
        Document(
            relative_path=Path("src/main.py"),
            content="print('hello world')",
            metadata={"source": "test"}
        )
    ]
    
    index_documents(
        documents=docs,
        project_config=project_config,
        state_dir=temp_state_dir,
        embed_model=mock_embed_model
    )
    
    store = get_storage_context(project_config, temp_state_dir).vector_store
    collection = store.client
    
    results = collection.get()
    
    assert len(results["ids"]) > 0
    assert results["metadatas"][0]["relative_path"] == "src/main.py"
    assert results["metadatas"][0]["source"] == "test"

def test_chunking_large_document(temp_state_dir, mock_embed_model, tmp_path):
    # Create a doc large enough to trigger chunking
    large_content = "Word. " * 2000
    docs = [
        Document(
            relative_path=Path("src/large.txt"),
            content=large_content,
            metadata={}
        )
    ]
    
    repo = tmp_path / "test-chunking"
    repo.mkdir()
    project_config = {"name": "test-chunking", "local_repository": str(repo)}
    index_documents(
        documents=docs,
        project_config=project_config,
        state_dir=temp_state_dir,
        embed_model=mock_embed_model
    )
    
    store = get_storage_context(project_config, temp_state_dir).vector_store
    collection = store.client
    results = collection.get()
    
    # Verify more than one node was produced for the same document
    assert len(results["ids"]) > 1
    # Verify all retain the relative_path
    for meta in results["metadatas"]:
        assert meta["relative_path"] == "src/large.txt"

def test_persistence_reopen(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "test-persist"
    repo.mkdir()
    project_config = {"name": "test-persist", "local_repository": str(repo)}
    
    docs = [
        Document(
            relative_path=Path("src/persist.py"),
            content="x = 1",
            metadata={}
        )
    ]
    
    index_documents(
        documents=docs,
        project_config=project_config,
        state_dir=temp_state_dir,
        embed_model=mock_embed_model
    )
    
    # Simulate completely new process/client by creating a new storage context
    storage_context = get_storage_context(project_config, temp_state_dir)
    collection = storage_context.vector_store.client
    results = collection.get()
    
    assert len(results["ids"]) > 0
    assert results["metadatas"][0]["relative_path"] == "src/persist.py"

def test_project_isolation(temp_state_dir, mock_embed_model, tmp_path):
    repo_a = tmp_path / "proj-a"
    repo_a.mkdir()
    proj_a = {"name": "Proj A", "local_repository": str(repo_a)}
    
    repo_b = tmp_path / "proj-b"
    repo_b.mkdir()
    proj_b = {"name": "Proj B", "local_repository": str(repo_b)}
    
    index_documents(
        documents=[Document(Path("a.txt"), "A", {})],
        project_config=proj_a,
        state_dir=temp_state_dir,
        embed_model=mock_embed_model
    )
    
    index_documents(
        documents=[Document(Path("b.txt"), "B", {})],
        project_config=proj_b,
        state_dir=temp_state_dir,
        embed_model=mock_embed_model
    )
    
    # Check A
    col_a = get_storage_context(proj_a, temp_state_dir).vector_store.client
    res_a = col_a.get()
    assert len(res_a["ids"]) > 0
    assert res_a["metadatas"][0]["relative_path"] == "a.txt"
    
    # Check B
    col_b = get_storage_context(proj_b, temp_state_dir).vector_store.client
    res_b = col_b.get()
    assert len(res_b["ids"]) > 0
    assert res_b["metadatas"][0]["relative_path"] == "b.txt"

def test_idempotent_reindexing(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "idempotent"
    repo.mkdir()
    project_config = {"name": "idempotent", "local_repository": str(repo)}
    docs = [Document(Path("idem.txt"), "content", {})]
    
    # First index
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    count_1 = len(col.get()["ids"])
    
    # Second index exact same
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    count_2 = len(col.get()["ids"])
    
    assert count_1 == count_2
    assert count_1 > 0

def test_changed_document_replacement(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "replace"
    repo.mkdir()
    project_config = {"name": "replace", "local_repository": str(repo)}
    
    # Original
    docs = [Document(Path("change.txt"), "old content", {})]
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    assert col.get()["documents"][0] == "old content"
    
    # Changed
    docs_changed = [Document(Path("change.txt"), "new content", {})]
    index_documents(docs_changed, project_config, temp_state_dir, mock_embed_model)
    
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    results = col.get()
    
    assert len(results["documents"]) == 1
    assert results["documents"][0] == "new content"

def test_repository_relative_metadata(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "metadata"
    repo.mkdir()
    project_config = {"name": "metadata", "local_repository": str(repo)}
    
    docs = [Document(Path("src/nested/file.py"), "code", {})]
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    meta = col.get()["metadatas"][0]
    
    assert meta["relative_path"] == "src/nested/file.py"
