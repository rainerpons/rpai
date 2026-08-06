from ai.providers.config import LanguageModelConfig
from ai import LanguageModel
from ai.providers.ollama.language_model import OllamaLanguageModel


def create_language_model(config: LanguageModelConfig) -> LanguageModel:
    if config.provider == "ollama":
        return OllamaLanguageModel(model=config.model)
        
    raise ValueError(f"Unsupported language model provider: '{config.provider}'")
