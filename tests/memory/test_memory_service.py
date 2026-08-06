import pytest
from unittest.mock import MagicMock, patch
from memory import create_memory_service, MemoryService, MemoryEntry, ProviderResponseError

def test_factory_creates_mem0_service_with_config():
    memory_config = {
        "provider": "mem0",
        "config": {"custom": "option"}
    }
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        service = create_memory_service(memory_config)
        assert isinstance(service, MemoryService)
        mock_memory_cls.from_config.assert_called_once_with({"custom": "option"})

def test_factory_creates_mem0_service_default_none():
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        service = create_memory_service(None)
        assert isinstance(service, MemoryService)
        mock_memory_cls.assert_called_once()
        mock_memory_cls.from_config.assert_not_called()

def test_factory_creates_mem0_service_empty_config():
    memory_config = {
        "provider": "mem0",
        "config": {}
    }
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        service = create_memory_service(memory_config)
        assert isinstance(service, MemoryService)
        mock_memory_cls.from_config.assert_called_once_with({})

def test_factory_unsupported_provider():
    memory_config = {
        "provider": "unsupported"
    }
    with pytest.raises(ValueError, match="Unsupported memory provider: 'unsupported'"):
        create_memory_service(memory_config)

def test_mem0_command_forwarding():
    mock_memory_instance = MagicMock()
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        service = create_memory_service({"provider": "mem0"})
        
        # create
        service.create("some text", user_id="user123", metadata={"key": "val"})
        mock_memory_instance.add.assert_called_once_with("some text", user_id="user123", metadata={"key": "val"})
        
        # update
        service.update("mem-id", "new text")
        mock_memory_instance.update.assert_called_once_with("mem-id", "new text")
        
        # delete
        service.delete("mem-id")
        mock_memory_instance.delete.assert_called_once_with("mem-id")

def test_mem0_search_happy_path():
    mock_memory_instance = MagicMock()
    mock_memory_instance.search.return_value = [
        {"id": "mem-1", "memory": "test memory 1", "metadata": {"key": "val"}},
        {"id": "mem-2", "text": "test memory 2", "metadata": None}
    ]
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        service = create_memory_service({"provider": "mem0"})
        
        results = service.search("query", user_id="user123")
        mock_memory_instance.search.assert_called_once_with("query", user_id="user123")
        
        assert len(results) == 2
        assert results[0] == MemoryEntry(id="mem-1", text="test memory 1", metadata={"key": "val"})
        assert results[1] == MemoryEntry(id="mem-2", text="test memory 2", metadata={})

def test_mem0_search_wrapped_results():
    mock_memory_instance = MagicMock()
    mock_memory_instance.search.return_value = {
        "results": [
            {"id": "mem-1", "memory": "test memory 1"}
        ]
    }
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        service = create_memory_service({"provider": "mem0"})
        results = service.search("query", user_id="user123")
        assert len(results) == 1
        assert results[0] == MemoryEntry(id="mem-1", text="test memory 1", metadata={})

def test_mem0_search_empty_results():
    mock_memory_instance = MagicMock()
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        service = create_memory_service({"provider": "mem0"})
        
        mock_memory_instance.search.return_value = []
        assert service.search("q", "u") == []
        
        mock_memory_instance.search.return_value = {"results": []}
        assert service.search("q", "u") == []

def test_mem0_search_malformed_responses():
    mock_memory_instance = MagicMock()
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        service = create_memory_service({"provider": "mem0"})
        
        # None result
        mock_memory_instance.search.return_value = None
        with pytest.raises(ProviderResponseError, match="Provider returned None"):
            service.search("q", "u")
            
        # Non list/dict result
        mock_memory_instance.search.return_value = "string result"
        with pytest.raises(ProviderResponseError, match="Unsupported provider response shape"):
            service.search("q", "u")
            
        # Dict missing results key
        mock_memory_instance.search.return_value = {"not_results": []}
        with pytest.raises(ProviderResponseError, match="missing required 'results' key"):
            service.search("q", "u")
            
        # Dict results is not a list
        mock_memory_instance.search.return_value = {"results": "not a list"}
        with pytest.raises(ProviderResponseError, match="'results' field is not a list"):
            service.search("q", "u")

def test_mem0_search_invalid_items():
    mock_memory_instance = MagicMock()
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        service = create_memory_service({"provider": "mem0"})
        
        # Item is not a dict
        mock_memory_instance.search.return_value = ["not a dict"]
        with pytest.raises(ProviderResponseError, match="Expected dictionary for memory item"):
            service.search("q", "u")
            
        # Item missing id
        mock_memory_instance.search.return_value = [{"memory": "some text"}]
        with pytest.raises(ProviderResponseError, match="missing required 'id' key"):
            service.search("q", "u")
            
        # Item id is not a string
        mock_memory_instance.search.return_value = [{"id": 123, "memory": "some text"}]
        with pytest.raises(ProviderResponseError, match="'id' must be a string"):
            service.search("q", "u")
            
        # Item missing content (both memory and text)
        mock_memory_instance.search.return_value = [{"id": "mem-1"}]
        with pytest.raises(ProviderResponseError, match="missing required content key"):
            service.search("q", "u")

        # Item text is not a string
        mock_memory_instance.search.return_value = [{"id": "mem-1", "memory": 123}]
        with pytest.raises(ProviderResponseError, match="content must be a string"):
            service.search("q", "u")
            
        # Metadata is not a dict
        mock_memory_instance.search.return_value = [{"id": "mem-1", "memory": "text", "metadata": "not a dict"}]
        with pytest.raises(ProviderResponseError, match="'metadata' must be a dictionary"):
            service.search("q", "u")

def test_mem0_provider_exception():
    mock_memory_instance = MagicMock()
    mock_memory_instance.search.side_effect = RuntimeError("Mem0 connection failed")
    with patch("memory.mem0_provider.Memory") as mock_memory_cls:
        mock_memory_cls.return_value = mock_memory_instance
        service = create_memory_service({"provider": "mem0"})
        with pytest.raises(RuntimeError, match="Mem0 connection failed"):
            service.search("q", "u")
