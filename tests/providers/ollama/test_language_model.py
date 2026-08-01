import pytest
from unittest.mock import patch, MagicMock

from workflow.context import Context, ContextEntry
from providers.ollama.language_model import OllamaLanguageModel


def test_ollama_language_model_rejects_empty_model():
    with pytest.raises(ValueError, match="Model cannot be empty."):
        OllamaLanguageModel(model="")


@patch("providers.ollama.language_model.ollama")
def test_ollama_language_model_generate_success(mock_ollama):
    mock_ollama.generate.return_value = {"response": "Generated text output"}
    
    model = OllamaLanguageModel(model="llama3.2:3b")
    context = Context(entries=(ContextEntry(source="test.py", content="content"),))
    
    result = model.generate(task="do it", context=context)
    
    assert result == "Generated text output"
    mock_ollama.generate.assert_called_once()
    
    kwargs = mock_ollama.generate.call_args.kwargs
    assert kwargs["model"] == "llama3.2:3b"
    assert "do it" in kwargs["prompt"]
    assert "test.py" in kwargs["prompt"]
    assert "content" in kwargs["prompt"]


@patch("providers.ollama.language_model.ollama")
def test_ollama_language_model_raises_runtime_error_on_empty_response(mock_ollama):
    mock_ollama.generate.return_value = {"response": ""}
    
    model = OllamaLanguageModel(model="llama3.2:3b")
    
    with pytest.raises(RuntimeError, match="No text was returned from Ollama."):
        model.generate(task="do it", context=Context())


@patch("providers.ollama.language_model.ollama")
def test_ollama_language_model_raises_runtime_error_on_missing_response_key(mock_ollama):
    mock_ollama.generate.return_value = {}
    
    model = OllamaLanguageModel(model="llama3.2:3b")
    
    with pytest.raises(RuntimeError, match="No text was returned from Ollama."):
        model.generate(task="do it", context=Context())
