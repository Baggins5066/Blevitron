import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from src.llm.service import LLMService

@pytest.mark.asyncio
async def test_generate_content():
    # Mock the aiohttp session
    mock_session = MagicMock()
    mock_post = AsyncMock()
    mock_session.post.return_value.__aenter__.return_value = mock_post
    mock_post.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "YES"
                        }
                    ]
                }
            }
        ]
    }
    mock_post.status = 200

    # Create an instance of the LLMService
    llm_service = LLMService()
    llm_service.session = mock_session

    # Call the generate_content method
    response = await llm_service.generate_content("test prompt", "test system instruction")

    # Assert that the response is correct
    assert response == "YES"
