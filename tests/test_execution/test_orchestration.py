from pathlib import Path
from collections.abc import Sequence

import pytest

import execution
from core.retrieval.models import RetrievalResult
from execution.models import WorkflowResult, ContextItem
from execution.orchestration import execute_task

class FakeLanguageModel:
    def __init__(self, return_text: str = "Fake output", raise_exception: Exception | None = None):
        self.return_text = return_text
        self.raise_exception = raise_exception
        self.received_task: str | None = None
        self.received_context: Sequence[ContextItem] | None = None

    def generate(self, *, task: str, context: Sequence[ContextItem]) -> str:
        self.received_task = task
        self.received_context = context
        if self.raise_exception:
            raise self.raise_exception
        return self.return_text

@pytest.fixture
def fake_project_config() -> dict:
    return {"local_repository": "/fake/repo"}

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

    custom_dir = Path("/custom/state")
    execute_task(task="task", project_config=fake_project_config, language_model=FakeLanguageModel(), state_dir=custom_dir)
    
    assert captured_state_dir == custom_dir

def test_transforms_retrieval_results_to_context_items(monkeypatch, fake_project_config):
    results = [
        RetrievalResult(text="1", metadata={"relative_path": "file1.txt"}, score=0.9),
        RetrievalResult(text="2", metadata={}, score=0.8),
    ]

    def fake_retrieve(query, project_config, top_k, state_dir):
        return results

    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)

    lm = FakeLanguageModel()
    execute_task(task="task", project_config=fake_project_config, language_model=lm)
    
    assert lm.received_context == [
        ContextItem(text="1", source="file1.txt"),
        ContextItem(text="2", source="unknown"),
    ]

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
    
    assert lm.received_context == []
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

def test_propagate_retrieval_exceptions(monkeypatch, fake_project_config):
    class FakeRetrievalError(Exception):
        pass

    def fake_retrieve(query, project_config, top_k, state_dir):
        raise FakeRetrievalError("Retrieval failed")

    monkeypatch.setattr("core.retrieval.retrieve_context", fake_retrieve)

    lm = FakeLanguageModel()
    with pytest.raises(FakeRetrievalError, match="Retrieval failed"):
        execute_task(task="task", project_config=fake_project_config, language_model=lm)
        
    assert lm.received_task is None

def test_propagate_language_model_exceptions(monkeypatch, fake_project_config):
    monkeypatch.setattr("core.retrieval.retrieve_context", lambda **kw: [])

    class FakeLMError(Exception):
        pass

    lm = FakeLanguageModel(raise_exception=FakeLMError("LM failed"))
    with pytest.raises(FakeLMError, match="LM failed"):
        execute_task(task="task", project_config=fake_project_config, language_model=lm)
