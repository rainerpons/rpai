from memory.service import MemoryService
from memory.mem0_provider import Mem0MemoryService

def create_memory_service(project_config: dict) -> MemoryService:
    """
    Factory function to create a MemoryService from project configuration.
    """
    memory_config = project_config.get("memory", {})
    provider = memory_config.get("provider", "mem0")
    
    if provider != "mem0":
        raise ValueError(f"Unsupported memory provider: '{provider}'")

    config = memory_config.get("config")
    return Mem0MemoryService(config)
