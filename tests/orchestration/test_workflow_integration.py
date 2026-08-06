import yaml


from llama_index.core.embeddings import MockEmbedding


from config import load_project_config
from context.indexing.index import index_documents
from context.ingestion.local_repo import ingest_local_repository

from orchestration import execute_task
from orchestration.models import TaskResult
from ai import Context

class FakeLanguageModel:
    def __init__(self, return_text: str = "Fake output", raise_exception: Exception | None = None):
        self.return_text = return_text
        self.raise_exception = raise_exception
        self.received_task: str | None = None
        self.received_context: Context | None = None

    def generate(self, *, task: str, context: Context) -> str:
        self.received_task = task
        self.received_context = context
        if self.raise_exception:
            raise self.raise_exception
        return self.return_text

class DeterministicTestEmbedding(MockEmbedding):
    def __init__(self):
        super().__init__(embed_dim=2)
        
    def _get_text_embedding(self, text: str) -> list[float]:
        vec = [0.0, 0.0]
        text_lower = text.lower()
        if "apple" in text_lower:
            vec[0] = 1.0
        if "orange" in text_lower:
            vec[1] = 1.0
        return vec
        
    def _get_query_embedding(self, query: str) -> list[float]:
        return self._get_text_embedding(query)

def test_workflow_integration(tmp_path, monkeypatch):
    # Initialize repository
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    (repo_dir / "src").mkdir()
    (repo_dir / "src" / "apple_module.py").write_text("def get_fruit():\n    return 'apple'\n")
    (repo_dir / "src" / "orange_module.py").write_text("def get_fruit():\n    return 'orange'\n")
    
    config_path = tmp_path / "project.yaml"
    config_data = {
        "name": "integration-project",
        "local_repository": str(repo_dir)
    }
    with config_path.open("w") as f:
        yaml.dump(config_data, f)
        
    loaded_config = load_project_config(config_path)
    
    # Index repository
    documents = list(ingest_local_repository(loaded_config))
    embed_model = DeterministicTestEmbedding()
    index_documents(documents, loaded_config, state_dir=state_dir, embed_model=embed_model)
    
    # Configure retrieval mock
    monkeypatch.setattr("context.retrieval.retrieve.get_default_embedding", lambda: DeterministicTestEmbedding())
    
    # Execute workflow
    lm = FakeLanguageModel(return_text="Integration success")
    
    task = "Tell me about apple"
    result = execute_task(
        task=task,
        project_config=loaded_config,
        language_model=lm,
        top_k=1,
        state_dir=state_dir
    )
    
    # Verify context transformation and workflow output
    assert isinstance(result, TaskResult)
    assert result.output == "Integration success"
    assert len(lm.received_context.entries) == 1
    assert lm.received_context.entries[0].source == "src/apple_module.py"
