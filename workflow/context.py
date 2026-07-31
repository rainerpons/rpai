from dataclasses import dataclass
from collections.abc import Sequence

@dataclass(frozen=True)
class ContextEntry:
    content: str
    source: str

@dataclass(frozen=True)
class Context:
    entries: Sequence[ContextEntry]
