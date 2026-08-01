from dataclasses import dataclass


@dataclass(frozen=True)
class ContextEntry:
    content: str
    source: str

@dataclass(frozen=True)
class Context:
    entries: tuple[ContextEntry, ...]
