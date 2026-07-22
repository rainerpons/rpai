from dataclasses import dataclass

@dataclass
class ValidationResult:
    success: bool
    message: str | None = None

class ValidationError(ValidationResult):
    def __init__(self, message: str | None = None):
        super().__init__(success=False, message=message)

class ValidationSuccess(ValidationResult):
    def __init__(self, message: str | None = None):
        super().__init__(success=True, message=message)
