from pathlib import Path


import pytest


from core.retrieval.models import RetrievalResult
from workflow.context import Context, ContextEntry
from workflow.models import WorkflowResult
from workflow.orchestration import execute_task, ProjectIndexError

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

@pytest.fixture
def fake_project_config(tmp_path) -> dict:
    repo = tmp_path / "fake_repo"
    repo.mkdir()
    return {"name": "test", "local_repository": str(repo)}

def test_reject_empty_task(fake_project_config):
    lm = FakeLanguageModel()
    with pytest.raises(ValueError, match="Task must not be empty."):
        execute_task(task="", project_config=fake_project_config, language_model=lm)
    assert lm.received_task is None

def test_reject_whitespace_only_task(fake_project_config):
    lm = FakeLanguageModel()
    with pytest.raises(ValueError, match="Task must not be empty."):
        execute_task(task="   \n\t ", project_config=fake_project_config, language_model=lm)
    assert lm.received_task is None

def test_retrieval_receives_original_task(monkeypatch, fake_project_config):
    captured_query = None

    def fake_retrieve(query, project_config, top_k, state_dir):
        nonlocal captured_query
        captured_query = query
        return []

    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)

    original_task = " Explain how indexing works, including chunking. "
    execute_task(task=original_task, project_config=fake_project_config, language_model=FakeLanguageModel())
    
    assert captured_query == original_task

def test_forward_project_config_to_retrieval(monkeypatch, fake_project_config):
    captured_config = None

    def fake_retrieve(query, project_config, top_k, state_dir):
        nonlocal captured_config
        captured_config = project_config
        return []

    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)

    execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel())
    
    assert captured_config is fake_project_config

def test_forward_top_k(monkeypatch, fake_project_config):
    captured_top_k = None

    def fake_retrieve(query, project_config, top_k, state_dir):
        nonlocal captured_top_k
        captured_top_k = top_k
        return []

    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)

    execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel(), top_k=42)
    
    assert captured_top_k == 42

def test_forward_state_dir(monkeypatch, fake_project_config):
    captured_state_dir = None

    def fake_retrieve(query, project_config, top_k, state_dir):
        nonlocal captured_state_dir
        captured_state_dir = state_dir
        return []

    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)
    monkeypatch.setattr("workflow.orchestration.ensure_project_index", lambda *a, **kw: None)

    custom_dir = Path("/custom/state")
    execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel(), state_dir=custom_dir)
    
    assert captured_state_dir == custom_dir

def test_transforms_retrieval_results_to_structured_context(monkeypatch, fake_project_config):
    results = [
        RetrievalResult(text="1", metadata={"relative_path": "file1.txt"}, score=0.9),
        RetrievalResult(text="2", metadata={}, score=0.8),
    ]

    def fake_retrieve(query, project_config, top_k, state_dir):
        return results

    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)

    lm = FakeLanguageModel()
    execute_task(task="task", project_config=fake_project_config, language_model=lm)
    
    expected_entries = (
        ContextEntry(content="1", source="file1.txt"),
        ContextEntry(content="2", source="unknown"),
    )
    assert lm.received_context == Context(entries=expected_entries)

def test_pass_original_task_to_language_model(monkeypatch, fake_project_config):
    monkeypatch.setattr("core.retrieval.retrieve_context", lambda **kw: [])

    lm = FakeLanguageModel()
    original_task = " Task with spaces "
    execute_task(task=original_task, project_config=fake_project_config, language_model=lm)
    
    assert lm.received_task == original_task

def test_execute_language_model_when_context_is_empty(monkeypatch, fake_project_config):
    monkeypatch.setattr("core.retrieval.retrieve_context", lambda **kw: [])

    lm = FakeLanguageModel(return_text="Answer to empty context")
    result = execute_task(task="task", project_config=fake_project_config, language_model=lm)
    
    assert lm.received_context == Context(entries=())
    assert result == WorkflowResult(output="Answer to empty context")

def test_wrap_generated_text_in_workflow_result(monkeypatch, fake_project_config):
    monkeypatch.setattr("core.retrieval.retrieve_context", lambda **kw: [])

    lm = FakeLanguageModel(return_text="Generated answer")
    result = execute_task(task="task", project_config=fake_project_config, language_model=lm)
    
    assert result == WorkflowResult(output="Generated answer")
    assert isinstance(result, WorkflowResult)

def test_preserve_generated_output_exactly(monkeypatch, fake_project_config):
    monkeypatch.setattr("core.retrieval.retrieve_context", lambda **kw: [])

    exact_output = " \n Generated answer \t "
    lm = FakeLanguageModel(return_text=exact_output)
    result = execute_task(task="task", project_config=fake_project_config, language_model=lm)
    
    assert result.output == exact_output

def test_propagate_language_model_exceptions(monkeypatch, fake_project_config):
    monkeypatch.setattr("core.retrieval.retrieve_context", lambda **kw: [])
    monkeypatch.setattr("workflow.orchestration.ensure_project_index", lambda *a, **kw: None)

    class FakeLMError(Exception):
        pass

    lm = FakeLanguageModel(raise_exception=FakeLMError("LM failed"))
    with pytest.raises(FakeLMError, match="LM failed"):
        execute_task(task="task", project_config=fake_project_config, language_model=lm)

def test_index_lifecycle_happy_path(monkeypatch, fake_project_config):
    calls = []
    
    monkeypatch.setattr("workflow.orchestration.ensure_project_index", lambda *a, **kw: calls.append("ensure"))
    monkeypatch.setattr("core.retrieval.retrieve_context", lambda **kw: calls.append("retrieve") or [])
    monkeypatch.setattr("workflow.orchestration.delete_project_index", lambda *a, **kw: calls.append("delete"))
    monkeypatch.setattr("workflow.orchestration.build_project_index", lambda *a, **kw: calls.append("build"))
    
    execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel())
    
    assert calls == ["ensure", "retrieve"]

def test_index_recovery_success(monkeypatch, fake_project_config):
    calls = []
    
    monkeypatch.setattr("workflow.orchestration.ensure_project_index", lambda *a, **kw: calls.append("ensure"))
    monkeypatch.setattr("workflow.orchestration.delete_project_index", lambda *a, **kw: calls.append("delete"))
    monkeypatch.setattr("workflow.orchestration.build_project_index", lambda *a, **kw: calls.append("build"))
    
    retrieval_calls = 0
    def fake_retrieve(**kw):
        nonlocal retrieval_calls
        retrieval_calls += 1
        calls.append(f"retrieve_{retrieval_calls}")
        if retrieval_calls == 1:
            raise RuntimeError("Corrupted index")
        return []
        
    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)
    
    execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel())
    
    assert calls == ["ensure", "retrieve_1", "delete", "build", "retrieve_2"]
    
def test_index_recovery_failure_raises_project_index_error(monkeypatch, fake_project_config):
    calls = []
    
    monkeypatch.setattr("workflow.orchestration.ensure_project_index", lambda *a, **kw: calls.append("ensure"))
    monkeypatch.setattr("workflow.orchestration.delete_project_index", lambda *a, **kw: calls.append("delete"))
    monkeypatch.setattr("workflow.orchestration.build_project_index", lambda *a, **kw: calls.append("build"))
    
    def fake_retrieve(**kw):
        calls.append("retrieve")
        raise RuntimeError("Corrupted index")
        
    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)
    
    with pytest.raises(ProjectIndexError, match="The project index could not be prepared"):
        execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel())
        
    assert calls == ["ensure", "retrieve", "delete", "build", "retrieve"]

def test_recovery_progress_messages(monkeypatch, fake_project_config):
    messages = []
    def progress(msg):
        messages.append(msg)
        
    monkeypatch.setattr("workflow.orchestration.ensure_project_index", lambda *a, **kw: None)
    monkeypatch.setattr("workflow.orchestration.delete_project_index", lambda *a, **kw: None)
    monkeypatch.setattr("workflow.orchestration.build_project_index", lambda *a, **kw: None)
    
    retrieval_calls = 0
    def fake_retrieve(**kw):
        nonlocal retrieval_calls
        retrieval_calls += 1
        if retrieval_calls == 1:
            raise RuntimeError("Corrupted")
        return []
        
    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)
    
    execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel(), progress=progress)
    
    assert messages == [
        "Existing project index could not be loaded. Rebuilding...",
        "Project index rebuilt."
    ]
