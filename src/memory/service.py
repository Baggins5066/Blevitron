from src.memory.storage import add_messages, search_similar_messages
from src.utils.logger import log
from colorama import Fore
import hashlib

class MemoryService:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def add_memory(self, author, message):
        embedding = await self.llm_service.generate_embedding(message)
        if embedding:
            message_id = hashlib.sha256(message.encode('utf-8')).hexdigest()
            add_messages([message], [embedding], [message_id], [author])
            log(f"[MEMORY] Added memory: {message}", Fore.MAGENTA)

    async def search_memories(self, query, limit=8):
        embedding = await self.llm_service.generate_embedding(query)
        if embedding:
            results = search_similar_messages(embedding, limit)
            return results
        return []
