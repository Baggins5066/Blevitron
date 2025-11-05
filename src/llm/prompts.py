from src.user.service import user_service
from src.memory.utils import get_relevant_memories
import json

class PromptStrategy:
    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def build_should_reply_prompt(self, message, history):
        processed_content = user_service.replace_aliases_with_usernames(message.content)
        processed_history = [
            {"author": h['author'], "content": user_service.replace_aliases_with_usernames(h['content'])}
            for h in history
        ]

        history_text = "\n".join([f"{h['author']}: {h['content']}" for h in processed_history[-10:]])
        memories = await get_relevant_memories(processed_content, processed_history, limit=40)
        memory_text = "\n".join([f"- {mem[0]}" for mem in memories])

        decision_prompt = f"""You are deciding whether "Botlivia Blevitron" (a Discord bot) should respond to this message.

Recent conversation:
{history_text}

Here are some relevant past messages from the database for context:
{memory_text}

Current message from {message.author}: {message.content}

Should the bot respond to this message?
Return only YES or NO.

Current message from {message.author}: {message.content}
Answer: """
        return decision_prompt

    async def build_llm_response_prompt(self, prompt, history=None, user_id=None):
        processed_prompt = user_service.replace_aliases_with_usernames(prompt)
        processed_history = [
            {"author": h['author'], "content": user_service.replace_aliases_with_usernames(h['content'])}
            for h in (history or [])
        ]

        try:
            current_message = processed_prompt.split("User: ")[-1] if "User: " in processed_prompt else processed_prompt
            memories = await get_relevant_memories(current_message, processed_history, limit=40)

            if memories:
                memory_text = "\n".join([f"- {mem}" for mem in memories])
                processed_prompt = f"[Relevant past messages for context]:\n{memory_text}\n\n{processed_prompt}"
        except Exception as e:
            # log error
            pass

        system_instruction = "You are Blevitron, user <@1430009844680884405>. Talk like the messages you see in the chat history."

        user_info = user_service.get_user_info(user_id)
        if user_info:
            system_instruction += f"\n\nThis is how you should act towards {user_info['username']}:\n{user_info['description']}"

        return processed_prompt, system_instruction
