from dataclasses import dataclass

@dataclass(frozen=True)
class ContextItem:
    text: str
    source: str

@dataclass(frozen=True)
class WorkflowResult:
    output: str
