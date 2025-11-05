import asyncio
from src.bot.bot import Bot
from src.config.settings import config
from src.utils.logger import log
from colorama import Fore

def main():
    if not config.DISCORD_BOT_TOKEN:
        log("[ERROR] DISCORD_BOT_TOKEN environment variable is not set!", Fore.RED)
        return
    if not config.LLM_API_KEY:
        log("[ERROR] LLM_API_KEY environment variable is not set!", Fore.RED)
        return

    bot = Bot()
    bot.run(config.DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    main()
