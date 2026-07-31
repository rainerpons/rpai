from typing import Protocol

from workflow.context import Context

class LanguageModel(Protocol):
    def generate(
        self,
        *,
        task: str,
        context: Context,
    ) -> str:
        ...
