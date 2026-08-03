from typing import Protocol

from orchestration.context import Context

class LanguageModel(Protocol):
    def generate(
        self,
        *,
        task: str,
        context: Context,
    ) -> str:
        ...
