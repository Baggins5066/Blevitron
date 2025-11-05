import aiohttp
import asyncio
import json
from colorama import Fore
from src.config.settings import config
from src.utils.logger import log

class LLMService:
    def __init__(self):
        self.session = aiohttp.ClientSession()
        self.headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": config.LLM_API_KEY
        }
        self.generate_content_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"
        self.embed_content_url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={config.LLM_API_KEY}"

    async def close(self):
        await self.session.close()

    async def _post(self, url, payload):
        max_retries = 3
        base_delay = 1
        for attempt in range(max_retries):
            try:
                async with self.session.post(url, headers=self.headers, data=json.dumps(payload)) as resp:
                    if resp.status == 503:
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            log(f"[LLM RETRY] API overloaded, retrying in {delay}s (attempt {attempt + 1}/{max_retries})", Fore.YELLOW)
                            await asyncio.sleep(delay)
                            continue
                        else:
                            log(f"[LLM ERROR] API still overloaded after {max_retries} attempts", Fore.RED)
                            return None

                    if resp.status != 200:
                        error_text = await resp.text()
                        log(f"[LLM ERROR] API returned status {resp.status}: {error_text}", Fore.RED)
                        return None

                    return await resp.json()
            except Exception as e:
                log(f"[LLM ERROR] Exception occurred: {type(e).__name__}: {e}", Fore.RED)
                import traceback
                log(f"[LLM ERROR] Traceback: {traceback.format_exc()}", Fore.RED)

                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    log(f"[LLM RETRY] Retrying in {delay}s (attempt {attempt + 1}/{max_retries})", Fore.YELLOW)
                    await asyncio.sleep(delay)
                    continue
        return None

    async def generate_content(self, prompt, system_instruction):
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "systemInstruction": {"parts": [{"text": system_instruction}]}
        }
        response_data = await self._post(self.generate_content_url, payload)
        if response_data and response_data.get("candidates"):
            return response_data["candidates"][0]["content"]["parts"][0]["text"]
        return None

    async def generate_embedding(self, text):
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{
                    "text": text
                }]
            }
        }
        response_data = await self._post(self.embed_content_url, payload)
        if response_data and response_data.get("embedding"):
            return response_data["embedding"]["values"]
        return None

async def should_bot_reply(message, history):
    from src.container import llm_service
    from src.llm.prompts import PromptStrategy
    prompt_strategy = PromptStrategy(llm_service)
    prompt = await prompt_strategy.build_should_reply_prompt(message, history)
    system_instruction = "You are a decision-making assistant. Respond with only YES or NO."
    decision = await llm_service.generate_content(prompt, system_instruction)
    log(f"[AI DECISION] Should reply: {decision}", Fore.YELLOW)
    return "YES" in decision.upper() if decision else False

async def get_llm_response(prompt, history=None, user_id=None):
    from src.container import llm_service
    from src.llm.prompts import PromptStrategy
    prompt_strategy = PromptStrategy(llm_service)
    processed_prompt, system_instruction = await prompt_strategy.build_llm_response_prompt(prompt, history, user_id)
    response = await llm_service.generate_content(processed_prompt, system_instruction)
    return response if response else "uh idk"
