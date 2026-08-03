from dataclasses import dataclass, field


@dataclass(frozen=True)
class ContextEntry:
    content: str
    source: str

@dataclass(frozen=True)
class Context:
    entries: tuple[ContextEntry, ...] = field(default_factory=tuple)
