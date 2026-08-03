from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class MemoryService(ABC):
    """
    Provider-independent memory service abstraction.
    Only exposes application-facing operations and types.
    """

    @abstractmethod
    def create(self, text: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create/add a new memory.
        
        Args:
            text: The text/fact to store.
            user_id: The ID of the user scope.
            metadata: Optional custom metadata.
            
        Returns:
            A dictionary containing the operation result (e.g. status, or created memory info).
        """
        pass

    @abstractmethod
    def retrieve(self, query: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve memories matching a query.
        
        Args:
            query: The semantic search query.
            user_id: The ID of the user scope.
            
        Returns:
            A list of memories, where each memory is represented as:
            {
                "id": str,
                "text": str,
                "metadata": Dict[str, Any]
            }
        """
        pass

    @abstractmethod
    def update(self, memory_id: str, text: str) -> None:
        """
        Update an existing memory.
        
        Args:
            memory_id: The ID of the memory to update.
            text: The new text to replace the existing memory.
        """
        pass

    @abstractmethod
    def delete(self, memory_id: str) -> None:
        """
        Delete a specific memory by its ID.
        
        Args:
            memory_id: The ID of the memory to delete.
        """
        pass
