import pytest
from pathlib import Path
from unittest.mock import patch

from llama_index.core.embeddings import MockEmbedding

from core.ingestion.models import Document
from core.indexing.store import get_storage_context, _get_project_storage_key
from core.indexing.index import index_documents, get_default_embedding

@pytest.fixture
def mock_embed_model():
    return MockEmbedding(embed_dim=10)

@pytest.fixture
def temp_state_dir(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    return state_dir

def test_project_storage_key(tmp_path):
    repo = tmp_path / "test-proj"
    repo.mkdir()
    assert "test-proj" in _get_project_storage_key({"name": "Test Project", "local_repository": str(repo)})

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

@patch("core.indexing.index.HuggingFaceEmbedding")
def test_default_embedding_model(mock_hf_embedding):
    get_default_embedding()
    mock_hf_embedding.assert_called_once_with(model_name="Alibaba-NLP/gte-modernbert-base")

def test_chunking_large_document(temp_state_dir, mock_embed_model, tmp_path):
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
    
    assert len(results["ids"]) > 1
    for meta in results["metadatas"]:
        assert meta["relative_path"] == "src/large.txt"

def test_persistence_reopen_and_skip_unchanged(temp_state_dir, tmp_path):
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
    
    embed_calls = []
    
    class TrackingMockEmbedding(MockEmbedding):
        def _get_text_embedding(self, text: str):
            embed_calls.append(text)
            return super()._get_text_embedding(text)
            
    track_embed = TrackingMockEmbedding(embed_dim=10)
    
    index_documents(docs, project_config, temp_state_dir, track_embed)
    initial_calls = len(embed_calls)
    assert initial_calls > 0
    
    store_context = get_storage_context(project_config, temp_state_dir)
    assert len(store_context.vector_store.client.get()["ids"]) > 0
    
    embed_calls.clear()
    index_documents(docs, project_config, temp_state_dir, track_embed)
    
    assert len(embed_calls) == 0

def test_project_isolation_same_name(temp_state_dir, mock_embed_model, tmp_path):
    repo_a = tmp_path / "a" / "backend"
    repo_a.mkdir(parents=True)
    proj_a = {"name": "backend", "local_repository": str(repo_a)}
    
    repo_b = tmp_path / "b" / "backend"
    repo_b.mkdir(parents=True)
    proj_b = {"name": "backend", "local_repository": str(repo_b)}
    
    index_documents(
        documents=[Document(Path("file.txt"), "A", {})],
        project_config=proj_a,
        state_dir=temp_state_dir,
        embed_model=mock_embed_model
    )
    
    index_documents(
        documents=[Document(Path("file.txt"), "B", {})],
        project_config=proj_b,
        state_dir=temp_state_dir,
        embed_model=mock_embed_model
    )
    
    col_a = get_storage_context(proj_a, temp_state_dir).vector_store.client
    res_a = col_a.get()
    assert len(res_a["ids"]) == 1
    assert res_a["documents"][0] == "A"
    
    col_b = get_storage_context(proj_b, temp_state_dir).vector_store.client
    res_b = col_b.get()
    assert len(res_b["ids"]) == 1
    assert res_b["documents"][0] == "B"

def test_idempotent_reindexing(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "idempotent"
    repo.mkdir()
    project_config = {"name": "idempotent", "local_repository": str(repo)}
    docs = [Document(Path("idem.txt"), "content", {})]
    
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    count_1 = len(col.get()["ids"])
    
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    count_2 = len(col.get()["ids"])
    
    assert count_1 == count_2
    assert count_1 > 0

def test_multi_chunk_replacement(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "replace"
    repo.mkdir()
    project_config = {"name": "replace", "local_repository": str(repo)}
    
    large_content = "This is a sentence. " * 1000
    docs = [Document(Path("change.txt"), large_content, {})]
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    original_results = col.get()
    original_chunk_count = len(original_results["ids"])
    assert original_chunk_count > 1
    
    docs_changed = [Document(Path("change.txt"), "new content only", {})]
    index_documents(docs_changed, project_config, temp_state_dir, mock_embed_model)
    
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    results = col.get()
    
    assert len(results["ids"]) == 1
    assert results["documents"][0] == "new content only"

def test_repository_relative_metadata(temp_state_dir, mock_embed_model, tmp_path):
    repo = tmp_path / "metadata"
    repo.mkdir()
    project_config = {"name": "metadata", "local_repository": str(repo)}
    
    docs = [Document(Path("src/nested/file.py"), "code", {})]
    index_documents(docs, project_config, temp_state_dir, mock_embed_model)
    
    col = get_storage_context(project_config, temp_state_dir).vector_store.client
    meta = col.get()["metadatas"][0]
    
    assert meta["relative_path"] == "src/nested/file.py"
