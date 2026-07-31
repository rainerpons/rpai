from typing import Protocol

from workflow.models import Context

class LanguageModel(Protocol):
    def generate(
        self,
        *,
        task: str,
        context: Context,
    ) -> str:
        ...
