from src.container import memory_service

async def get_relevant_memories(current_message, conversation_history, limit=40):
    """
    Get relevant memories based on current message and recent conversation.

    Args:
        current_message: The current message text
        conversation_history: List of recent messages for context
        limit: Number of memories to retrieve

    Returns:
        List of relevant message strings
    """
    # Combine current message with recent context for better search
    context = " ".join([msg.get('content', '') for msg in conversation_history[-3:]])
    search_query = f"{context} {current_message}"

    # Search for similar messages
    results = await memory_service.search_memories(search_query, limit)

    # Extract just the message content, ignoring the author from the tuple
    memories = [content for content, similarity, _ in results if similarity > 0.3]

    return memories
