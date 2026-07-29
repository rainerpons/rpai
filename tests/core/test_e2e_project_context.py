import pytest
from pathlib import Path
import yaml
import chromadb

from core.config import load_project_config
from core.ingestion.local_repo import ingest_local_repository
from core.indexing.index import index_documents
from core.retrieval.retrieve import retrieve_context
from llama_index.core.embeddings import MockEmbedding

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

def test_e2e_project_context_pipeline(tmp_path):
    # Setup test environment
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    
    # Create some repository content
    (repo_dir / "src").mkdir()
    (repo_dir / "src" / "apple_module.py").write_text("def get_fruit():\n    return 'apple'\n")
    (repo_dir / "src" / "orange_module.py").write_text("def get_fruit():\n    return 'orange'\n")
    (repo_dir / "docs").mkdir()
    (repo_dir / "docs" / "info.txt").write_text("This project has apple and orange modules.")
    
    # Create project configuration
    config_path = tmp_path / "project.yaml"
    config_data = {
        "name": "e2e-test-project",
        "local_repository": str(repo_dir)
    }
    with config_path.open("w") as f:
        yaml.dump(config_data, f)
        
    # Step A: Load, ingest, index, and persist
    loaded_config = load_project_config(config_path)
    assert loaded_config["name"] == "e2e-test-project"
    
    documents = list(ingest_local_repository(loaded_config))
    assert len(documents) == 3
    
    embed_model = DeterministicTestEmbedding()
    
    # indexing will persist to state_dir
    index_documents(documents, loaded_config, state_dir=state_dir, embed_model=embed_model)
    
    # Step B: Retrieval across a real process boundary
    # We spawn a completely separate Python process to ensure we are querying
    # the persisted state on disk rather than any in-memory objects.
    
    retrieval_script = tmp_path / "run_retrieval.py"
    retrieval_script.write_text(f"""
import sys
import json
from pathlib import Path
from core.config import load_project_config
from core.retrieval.retrieve import retrieve_context

# We need the same deterministic embedding model to query the index
from tests.core.test_e2e_project_context import DeterministicTestEmbedding

config_path = "{config_path}"
state_dir = Path("{state_dir}")
loaded_config = load_project_config(config_path)

embed_model = DeterministicTestEmbedding()

results = retrieve_context(
    query="apple",
    project_config=loaded_config,
    top_k=2,
    state_dir=state_dir,
    embed_model=embed_model
)

output = []
for res in results:
    output.append({{
        "text": res.text,
        "relative_path": res.metadata.get("relative_path")
    }})

with open("{tmp_path / 'retrieval_results.json'}", "w") as f:
    json.dump(output, f)
""")

    import subprocess
    import sys
    
    # Run the retrieval script in a separate process
    import os
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent)
    
    result = subprocess.run(
        [sys.executable, str(retrieval_script)],
        capture_output=True,
        text=True,
        env=env
    )
    
    assert result.returncode == 0, f"Retrieval script failed:\n{{result.stderr}}"
    
    import json
    with open(tmp_path / "retrieval_results.json") as f:
        retrieved_data = json.load(f)
        
    assert len(retrieved_data) > 0
    assert any("apple" in item["text"].lower() for item in retrieved_data)
    
    # Verify metadata is repository-relative
    metadata_paths = [item["relative_path"] for item in retrieved_data]
    assert "src/apple_module.py" in metadata_paths or "docs/info.txt" in metadata_paths
    
    # Ensure orange is not retrieved when asking for apple
    assert "src/orange_module.py" not in metadata_paths
