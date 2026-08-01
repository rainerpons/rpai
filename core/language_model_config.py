from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class LanguageModelConfig:
    provider: str
    model: str


def load_language_model_config(project_config: Dict[str, Any]) -> LanguageModelConfig:
    if "language_model" not in project_config:
        raise ValueError("Configuration 'language_model' must exist.")
    
    lm_config = project_config["language_model"]
    if not isinstance(lm_config, dict):
        raise ValueError("Configuration 'language_model' must be a mapping.")
    
    provider = lm_config.get("provider")
    if provider != "ollama":
        raise ValueError("Configuration 'provider' must equal 'ollama'.")
    
    model = lm_config.get("model")
    if not isinstance(model, str) or not model:
        raise ValueError("Configuration 'model' must be a non-empty string.")
    
    return LanguageModelConfig(provider=provider, model=model)
