import pytest
from pathlib import Path

from llama_index.core.embeddings import MockEmbedding

from core.ingestion.models import Document
from core.indexing.index import index_documents
from core.retrieval.retrieve import retrieve_context

class DeterministicTestEmbedding(MockEmbedding):
    """
    A simple embedding model that creates vectors where we can deterministically
    distinguish content based on keywords for retrieval tests.
    """
    def __init__(self):
        super().__init__(embed_dim=2)
        
    def _get_text_embedding(self, text: str) -> list[float]:
        # Dimension 0: 'apple'
        # Dimension 1: 'orange'
        vec = [0.0, 0.0]
        text_lower = text.lower()
        if "apple" in text_lower:
            vec[0] = 1.0
        if "orange" in text_lower:
            vec[1] = 1.0
        return vec
        
    def _get_query_embedding(self, query: str) -> list[float]:
        return self._get_text_embedding(query)

@pytest.fixture
def test_embed_model():
    return DeterministicTestEmbedding()

@pytest.fixture
def temp_state_dir(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    return state_dir

@pytest.fixture
def project_config(tmp_path):
    repo = tmp_path / "test-proj"
    repo.mkdir()
    return {"name": "test-proj", "local_repository": str(repo)}

def test_retrieves_semantically_relevant_indexed_content(temp_state_dir, test_embed_model, project_config):

    doc1 = Document(Path("file1.txt"), "This is about apples.", {})
    doc2 = Document(Path("file2.txt"), "This is about oranges.", {})
    
    index_documents([doc1, doc2], project_config, temp_state_dir, test_embed_model)
    
    results = retrieve_context(
        query="tell me about apples",
        project_config=project_config,
        top_k=1,
        state_dir=temp_state_dir,
        embed_model=test_embed_model
    )
    
    assert len(results) == 1
    assert "apples" in results[0].text.lower()
    
def test_preserves_repository_relative_source_metadata(temp_state_dir, test_embed_model, project_config):

    doc = Document(Path("src/fruit.txt"), "apple", {})
    index_documents([doc], project_config, temp_state_dir, test_embed_model)
    
    results = retrieve_context(
        query="apple",
        project_config=project_config,
        top_k=1,
        state_dir=temp_state_dir,
        embed_model=test_embed_model
    )
    
    assert len(results) == 1
    assert results[0].metadata["relative_path"] == "src/fruit.txt"
    
def test_respects_top_k(temp_state_dir, test_embed_model, project_config):

    docs = [
        Document(Path(f"file{i}.txt"), "apple", {}) for i in range(5)
    ]
    index_documents(docs, project_config, temp_state_dir, test_embed_model)
    
    results = retrieve_context(
        query="apple",
        project_config=project_config,
        top_k=2,
        state_dir=temp_state_dir,
        embed_model=test_embed_model
    )
    
    assert len(results) == 2
    
def test_project_isolation(temp_state_dir, test_embed_model, tmp_path):
    repo_a = tmp_path / "proj-a"
    repo_a.mkdir()
    proj_a = {"name": "proj-a", "local_repository": str(repo_a)}

    repo_b = tmp_path / "proj-b"
    repo_b.mkdir()
    proj_b = {"name": "proj-b", "local_repository": str(repo_b)}

    index_documents([Document(Path("a.txt"), "apple project A", {})], proj_a, temp_state_dir, test_embed_model)
    index_documents([Document(Path("b.txt"), "apple project B", {})], proj_b, temp_state_dir, test_embed_model)

    results = retrieve_context(
        query="apple",
        project_config=proj_a,
        top_k=5,
        state_dir=temp_state_dir,
        embed_model=test_embed_model
    )
    
    assert len(results) == 1
    assert "project A" in results[0].text
    assert "project B" not in results[0].text

def test_retrieval_survives_reopening_persisted_storage(temp_state_dir, test_embed_model, project_config):

    doc = Document(Path("file.txt"), "apple", {})
    index_documents([doc], project_config, temp_state_dir, test_embed_model)
    
    results = retrieve_context(
        query="apple",
        project_config=project_config,
        top_k=5,
        state_dir=temp_state_dir,
        embed_model=test_embed_model
    )
    
    assert len(results) == 1
    assert "apple" in results[0].text

def test_rejects_empty_query(temp_state_dir, test_embed_model, project_config):

    with pytest.raises(ValueError, match="whitespace"):
        retrieve_context("", project_config, state_dir=temp_state_dir, embed_model=test_embed_model)

    with pytest.raises(ValueError, match="whitespace"):
        retrieve_context("   ", project_config, state_dir=temp_state_dir, embed_model=test_embed_model)

def test_rejects_invalid_top_k(temp_state_dir, test_embed_model, project_config):

    with pytest.raises(ValueError, match="top_k"):
        retrieve_context("query", project_config, top_k=0, state_dir=temp_state_dir, embed_model=test_embed_model)

    with pytest.raises(ValueError, match="top_k"):
        retrieve_context("query", project_config, top_k=-1, state_dir=temp_state_dir, embed_model=test_embed_model)

def test_empty_project_index(temp_state_dir, test_embed_model, project_config):
    results = retrieve_context(
        query="apple",
        project_config=project_config,
        top_k=5,
        state_dir=temp_state_dir,
        embed_model=test_embed_model
    )
    
    assert results == []
