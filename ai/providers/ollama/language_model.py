import ollama

from ai import Context, LanguageModel
from ai.providers.ollama.prompt import build_prompt


class OllamaLanguageModel(LanguageModel):
    def __init__(self, *, model: str):
        if not model:
            raise ValueError("Model cannot be empty.")
        self.model = model

    def generate(self, *, task: str, context: Context) -> str:
        prompt = build_prompt(task, context)
        
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
        )
        
        if not response or "response" not in response:
            raise RuntimeError("No text was returned from Ollama.")
            
        generated_text = response["response"]
        
        if not generated_text:
            raise RuntimeError("No text was returned from Ollama.")
            
        return generated_text
