import discord
from discord.ext import commands
from collections import deque
from colorama import Fore

from src.utils.logger import log

class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

        self.conversation_history = {}
        self.processed_messages = deque(maxlen=1000)

    async def on_ready(self):
        if self.user:
            log(f"[READY] Logged in as {self.user} (ID: {self.user.id})", Fore.GREEN)

            log("Connected to the following servers:", Fore.YELLOW)
            for guild in self.guilds:
                log(f"- {guild.name} (ID: {guild.id})", Fore.YELLOW)

            try:
                await self.load_extension("src.bot.cogs.commands")
                synced = await self.tree.sync()
                log(f"Synced {len(synced)} command(s)", Fore.GREEN)
            except Exception as e:
                log(f"Failed to sync commands: {e}", Fore.RED)
