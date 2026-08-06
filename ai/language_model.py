from typing import Protocol

from ai.context import Context

class LanguageModel(Protocol):
    def generate(
        self,
        *,
        task: str,
        context: Context,
    ) -> str:
        ...
