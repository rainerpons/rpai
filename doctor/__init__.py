from dataclasses import dataclass

@dataclass
class ValidationResult:
    success: bool
    message: str | None = None
