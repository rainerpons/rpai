from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class RetrievalResult:
    text: str
    metadata: dict[str, Any]
    score: float | None = None
