from typing import List, Dict, Any, Optional
from mem0 import Memory
from memory.service import MemoryService, MemoryEntry, ProviderResponseError

class Mem0MemoryService(MemoryService):
    """Mem0-backed implementation of the memory service interface."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        if config is None:
            self.client = Memory()
        else:
            self.client = Memory.from_config(config)

    def create(self, text: str, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.client.add(text, user_id=user_id, metadata=metadata)

    def _normalize_results(self, results: Any) -> List[MemoryEntry]:
        """Normalize supported Mem0 response shapes into a list of MemoryEntry objects."""
        if results is None:
            raise ProviderResponseError("Provider returned None instead of a valid search response.")

        if isinstance(results, dict):
            if "results" not in results:
                raise ProviderResponseError(f"Provider response dictionary is missing required 'results' key. Received: {results}")
            results_list = results["results"]
            if not isinstance(results_list, list):
                raise ProviderResponseError(f"Provider 'results' field is not a list. Received type: {type(results_list).__name__}")
        elif isinstance(results, list):
            results_list = results
        else:
            raise ProviderResponseError(f"Unsupported provider response shape: expected list or dict, got {type(results).__name__}. Received: {results}")

        mapped = []
        for item in results_list:
            if not isinstance(item, dict):
                raise ProviderResponseError(f"Expected dictionary for memory item in provider response, got {type(item).__name__}")
            
            memory_id = item.get("id")
            if memory_id is None:
                raise ProviderResponseError(f"Memory item is missing required 'id' key: {item}")
            if not isinstance(memory_id, str):
                raise ProviderResponseError(f"Memory item 'id' must be a string, got {type(memory_id).__name__}")

            text = item.get("memory")
            if text is None:
                text = item.get("text")
            if text is None:
                raise ProviderResponseError(f"Memory item is missing required content key ('memory' or 'text'): {item}")
            if not isinstance(text, str):
                raise ProviderResponseError(f"Memory item content must be a string, got {type(text).__name__}")

            metadata = item.get("metadata")
            if metadata is not None and not isinstance(metadata, dict):
                raise ProviderResponseError(f"Memory item 'metadata' must be a dictionary, got {type(metadata).__name__}")

            mapped.append(MemoryEntry(
                id=memory_id,
                text=text,
                metadata=metadata if metadata is not None else {}
            ))
        return mapped

    def search(self, query: str, user_id: str) -> List[MemoryEntry]:
        results = self.client.search(query, user_id=user_id)
        return self._normalize_results(results)

    def update(self, memory_id: str, text: str) -> None:
        self.client.update(memory_id, text)

    def delete(self, memory_id: str) -> None:
        self.client.delete(memory_id)
