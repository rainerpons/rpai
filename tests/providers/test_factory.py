import pytest

from providers.factory import create_language_model
from providers.ollama.language_model import OllamaLanguageModel


def test_create_language_model_success():
    config = {
        "language_model": {
            "provider": "ollama",
            "model": "llama3.2:3b"
        }
    }
    
    model = create_language_model(config)
    
    assert isinstance(model, OllamaLanguageModel)
    assert model.model == "llama3.2:3b"


def test_create_language_model_unsupported_provider():
    config = {
        "language_model": {
            "provider": "openai",
            "model": "gpt-4"
        }
    }
    
    with pytest.raises(ValueError, match="Configuration 'provider' must equal 'ollama'."):
        create_language_model(config)
