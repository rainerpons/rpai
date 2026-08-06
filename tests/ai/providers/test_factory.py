import pytest

from ai.providers.config import LanguageModelConfig
from ai.providers.factory import create_language_model
from ai.providers.ollama.language_model import OllamaLanguageModel


def test_create_language_model_success():
    config = LanguageModelConfig(provider="ollama", model="llama3.2:3b")
    
    model = create_language_model(config)
    
    assert isinstance(model, OllamaLanguageModel)
    assert model.model == "llama3.2:3b"


def test_create_language_model_unsupported_provider():
    config = LanguageModelConfig(provider="openai", model="gpt-4")
    
    with pytest.raises(ValueError, match="Unsupported language model provider: 'openai'"):
        create_language_model(config)
