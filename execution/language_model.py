from typing import Protocol
from collections.abc import Sequence

from execution.models import ContextItem

class LanguageModel(Protocol):
    def generate(
        self,
        *,
        task: str,
        context: Sequence[ContextItem],
    ) -> str:
        ...
