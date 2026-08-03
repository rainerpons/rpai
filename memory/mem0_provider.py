from typing import List, Dict, Any, Optional
from mem0 import Memory
from memory.service import MemoryService

class Mem0MemoryService(MemoryService):
    """Mem0-backed implementation of the memory service interface."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config:
            self.client = Memory.from_config(config)
        else:
            self.client = Memory()

    def create(self, text: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.client.add(text, user_id=user_id, metadata=metadata)

    def _normalize_results(self, results: Any) -> List[Dict[str, Any]]:
        """Normalize supported Mem0 response shapes into memory result dictionaries."""
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

    def retrieve(self, query: str, user_id: str) -> List[Dict[str, Any]]:
        results = self.client.search(query, user_id=user_id)
        return self._normalize_results(results)

    def update(self, memory_id: str, text: str) -> None:
        self.client.update(memory_id, text)

    def delete(self, memory_id: str) -> None:
        self.client.delete(memory_id)
