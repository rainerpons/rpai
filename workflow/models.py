from dataclasses import dataclass

@dataclass(frozen=True)
class Context:
    content: str

@dataclass(frozen=True)
class WorkflowResult:
    output: str
