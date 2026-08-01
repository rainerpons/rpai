import pytest
from core.language_model_config import load_language_model_config, LanguageModelConfig


def test_load_valid_language_model_config():
    config = {
        "language_model": {
            "provider": "ollama",
            "model": "llama3.2:3b"
        }
    }
    result = load_language_model_config(config)
    assert isinstance(result, LanguageModelConfig)
    assert result.provider == "ollama"
    assert result.model == "llama3.2:3b"


def test_load_missing_language_model():
    config = {}
    with pytest.raises(ValueError, match="Configuration 'language_model' must exist."):
        load_language_model_config(config)


def test_load_language_model_not_mapping():
    config = {"language_model": "ollama"}
    with pytest.raises(ValueError, match="Configuration 'language_model' must be a mapping."):
        load_language_model_config(config)


def test_load_invalid_provider():
    config = {
        "language_model": {
            "provider": "openai",
            "model": "gpt-4"
        }
    }
    with pytest.raises(ValueError, match="Configuration 'provider' must equal 'ollama'."):
        load_language_model_config(config)


def test_load_missing_model():
    config = {
        "language_model": {
            "provider": "ollama"
        }
    }
    with pytest.raises(ValueError, match="Configuration 'model' must be a non-empty string."):
        load_language_model_config(config)


def test_load_blank_model():
    config = {
        "language_model": {
            "provider": "ollama",
            "model": ""
        }
    }
    with pytest.raises(ValueError, match="Configuration 'model' must be a non-empty string."):
        load_language_model_config(config)
