from dataclasses import dataclass

# TODO: Evolve this to include execution metadata (e.g. citations, token usage, timing)
@dataclass(frozen=True)
class WorkflowResult:
    output: str
