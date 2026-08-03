import pytest
from unittest.mock import MagicMock, patch
from memory import create_memory_service
from memory.service import MemoryService

def test_factory_creates_mem0_service():
    project_config = {
        "memory": {
            "provider": "mem0",
            "config": {"custom": "option"}
        }
    }
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        service = create_memory_service(project_config)
        assert isinstance(service, MemoryService)
        mock_memory_cls.from_config.assert_called_once_with({"custom": "option"})

def test_factory_unsupported_provider():
    project_config = {
        "memory": {
            "provider": "unsupported"
        }
    }
    with pytest.raises(ValueError, match="Unsupported memory provider: 'unsupported'"):
        create_memory_service(project_config)

def test_mem0_crud_operations():
    mock_memory_instance = MagicMock()
    mock_memory_instance.add.return_value = {"status": "success"}
    mock_memory_instance.search.return_value = [
        {"id": "mem-1", "memory": "test memory 1", "metadata": {"key": "val"}},
        {"id": "mem-2", "memory": "test memory 2", "metadata": None}
    ]

    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        
        service = create_memory_service({})
        
        # Create
        create_result = service.create("test memory 1", user_id="user1")
        assert create_result == {"status": "success"}
        mock_memory_instance.add.assert_called_once_with("test memory 1", user_id="user1", metadata=None)
        
        # Retrieve
        retrieved = service.retrieve("query", user_id="user1")
        assert len(retrieved) == 2
        assert retrieved[0] == {"id": "mem-1", "text": "test memory 1", "metadata": {"key": "val"}}
        assert retrieved[1] == {"id": "mem-2", "text": "test memory 2", "metadata": {}}
        mock_memory_instance.search.assert_called_once_with("query", user_id="user1")
        
        # Update
        service.update("mem-1", "new text")
        mock_memory_instance.update.assert_called_once_with("mem-1", "new text")
        
        # Delete
        service.delete("mem-1")
        mock_memory_instance.delete.assert_called_once_with("mem-1")
