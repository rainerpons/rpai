from typing import Any, Dict

from core.language_model_config import load_language_model_config
from workflow.language_model import LanguageModel
from providers.ollama.language_model import OllamaLanguageModel


def create_language_model(project_config: Dict[str, Any]) -> LanguageModel:
    config = load_language_model_config(project_config)
    
    if config.provider == "ollama":
        return OllamaLanguageModel(model=config.model)
        
    # The config parser currently restricts provider to 'ollama'
    # but for completeness we can raise an error here too if we ever bypass it.
    raise ValueError(f"Unsupported language model provider: '{config.provider}'")
