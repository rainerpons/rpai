from typing import Optional
from memory.service import MemoryService
from memory.mem0_provider import Mem0MemoryService

def create_memory_service(memory_config: Optional[dict] = None) -> MemoryService:
    """
    Factory function to create a MemoryService from memory configuration.
    """
    if memory_config is None:
        memory_config = {}
        
    provider = memory_config.get("provider", "mem0")
    
    if provider != "mem0":
        raise ValueError(f"Unsupported memory provider: '{provider}'")

    config = memory_config.get("config")
    return Mem0MemoryService(config)
