from typing import List, Dict, Any, Optional
from mem0 import Memory
from memory.service import MemoryService

class Mem0MemoryService(MemoryService):
    """
    Mem0-backed implementation of MemoryService.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Mem0 memory provider.
        
        Args:
            config: A configuration dictionary to initialize Mem0.
        """
        if config:
            self.client = Memory.from_config(config)
        else:
            self.client = Memory()

    def create(self, text: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create/add a new memory.
        """
        return self.client.add(text, user_id=user_id, metadata=metadata)

    def retrieve(self, query: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve memories matching a query.
        """
        results = self.client.search(query, user_id=user_id)
        
        if isinstance(results, dict) and "results" in results:
            results_list = results["results"]
        elif isinstance(results, list):
            results_list = results
        else:
            results_list = []
            
        mapped = []
        for item in results_list:
            if not isinstance(item, dict):
                continue
            mapped.append({
                "id": item.get("id", ""),
                "text": item.get("memory", item.get("text", "")),
                "metadata": item.get("metadata") or {}
            })
        return mapped

    def update(self, memory_id: str, text: str) -> None:
        """
        Update an existing memory.
        """
        self.client.update(memory_id, text)

    def delete(self, memory_id: str) -> None:
        """
        Delete a specific memory by its ID.
        """
        self.client.delete(memory_id)
