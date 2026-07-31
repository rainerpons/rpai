from dataclasses import dataclass

@dataclass(frozen=True)
class WorkflowResult:
    output: str
