from src.llm.service import LLMService
from src.memory.service import MemoryService

llm_service = LLMService()
memory_service = MemoryService(llm_service)
