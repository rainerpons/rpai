from typing import Protocol
from collections.abc import Sequence

from core.retrieval.models import RetrievalResult

class LanguageModel(Protocol):
    def generate(
        self,
        *,
        task: str,
        context: Sequence[RetrievalResult],
    ) -> str:
        ...
