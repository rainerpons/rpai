from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class RetrievalResult:
    text: str
    metadata: Dict[str, Any]
    score: Optional[float] = None
