from typing import Protocol, List, Dict, Any, Optional, runtime_checkable
from dataclasses import dataclass, field

@dataclass(frozen=True)
class MemoryEntry:
    """Represent a retrieved memory entry."""
    id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class MemoryProviderResponseError(Exception):
    """Raised when the memory provider returns a malformed or unsupported response."""
    pass

@runtime_checkable
class MemoryService(Protocol):
    """
    Provider-independent memory service interface.
    Only exposes application-facing operations and types.
    """

    def create(self, text: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Create a new memory.
        
        Args:
            text: The text/fact to store.
            user_id: The ID of the user scope.
            metadata: Optional custom metadata.
        """
        ...

    def search(self, query: str, user_id: str) -> List[MemoryEntry]:
        """
        Search memories matching a query.
        
        Args:
            query: The semantic search query.
            user_id: The ID of the user scope.
            
        Returns:
            A list of MemoryEntry objects.
        """
        ...

    def update(self, memory_id: str, text: str) -> None:
        """
        Update an existing memory.
        
        Args:
            memory_id: The ID of the memory to update.
            text: The new text to replace the existing memory.
        """
        ...

    def delete(self, memory_id: str) -> None:
        """
        Delete a specific memory by its ID.
        
        Args:
            memory_id: The ID of the memory to delete.
        """
        ...
