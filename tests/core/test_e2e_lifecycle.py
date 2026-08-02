import pytest
import yaml
import subprocess
import sys
import json
from pathlib import Path

def test_e2e_lifecycle(tmp_path):
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    (repo_dir / "src.py").write_text("x = 1")
    
    config_path = tmp_path / "project.yaml"
    with config_path.open("w") as f:
        yaml.dump({"name": "e2e-life", "local_repository": str(repo_dir)}, f)

    script_path = tmp_path / "run.py"
    script_path.write_text(f"""
import json
import sys
from pathlib import Path
from core.config import load_project_config
from workflow.orchestration import execute_task
from llama_index.core.embeddings import MockEmbedding

class FakeLanguageModel:
    def generate(self, *, task, context):
        return "fake response"
        
loaded_config = load_project_config(Path("{config_path}"))
lm = FakeLanguageModel()

import core.indexing.index
import core.retrieval.retrieve
core.indexing.index.get_default_embedding = lambda: MockEmbedding(embed_dim=2)
core.retrieval.retrieve.get_default_embedding = lambda: MockEmbedding(embed_dim=2)

progress_calls = []
try:
    res = execute_task("my task", loaded_config, lm, state_dir=Path("{state_dir}"), progress=lambda m: progress_calls.append(m))
    with open("{tmp_path}/res.json", "w") as f:
        json.dump({{"output": res.output, "progress": progress_calls}}, f)
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
""")

    subprocess.run([sys.executable, str(script_path)], check=True)
    with open(tmp_path / "res.json") as f:
        data1 = json.load(f)
    assert data1["output"] == "fake response"
    assert "Creating project index..." in data1["progress"]
    
    (tmp_path / "res.json").unlink()
    subprocess.run([sys.executable, str(script_path)], check=True)
    with open(tmp_path / "res.json") as f:
        data2 = json.load(f)
    assert data2["output"] == "fake response"
    assert "Creating project index..." not in data2["progress"]
    
    project_keys = list((state_dir / "chroma").iterdir())
    assert len(project_keys) == 1
    docstore_file = project_keys[0] / "docstore.json"
    docstore_file.write_text("{ corrupt json")
    
    (tmp_path / "res.json").unlink()
    subprocess.run([sys.executable, str(script_path)], check=True)
    with open(tmp_path / "res.json") as f:
        data3 = json.load(f)
    assert data3["output"] == "fake response"
    assert "Existing project index could not be loaded. Rebuilding..." in data3["progress"]
    assert "Project index rebuilt." in data3["progress"]
