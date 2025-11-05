import pytest
from unittest.mock import MagicMock, AsyncMock
from src.memory.service import MemoryService
from src.llm.service import LLMService

@pytest.mark.asyncio
async def test_add_memory():
    # Mock the LLMService
    mock_llm_service = MagicMock(spec=LLMService)
    mock_llm_service.generate_embedding = AsyncMock(return_value=[0.1, 0.2, 0.3])

    # Mock the ChromaDB storage
    mock_add_messages = MagicMock()

    # Create an instance of the MemoryService
    memory_service = MemoryService(mock_llm_service)
    memory_service.add_messages = mock_add_messages

    # Call the add_memory method
    await memory_service.add_memory("test_author", "test_message")

    # Assert that the generate_embedding method was called
    mock_llm_service.generate_embedding.assert_called_once_with("test_message")
