from discord.ext import commands
from discord import app_commands
import discord
import asyncio
from collections import deque
from colorama import Fore

from src.utils.logger import log
from src.utils.helpers import replace_with_mentions
from src.llm.service import should_bot_reply, get_llm_response

class SleepCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_sleeping = False

    @app_commands.command(name="sleep", description="Make the bot go to sleep for a specified number of minutes.")
    @app_commands.describe(minutes="The number of minutes for the bot to sleep.")
    async def sleep(self, interaction: discord.Interaction, minutes: int):
        self.is_sleeping = True
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(name="Sleeping..."))
        await interaction.response.send_message(f"Going to sleep for {minutes} minutes...", ephemeral=True)

        await asyncio.sleep(minutes * 60)

        self.is_sleeping = False
        await self.bot.change_presence(status=discord.Status.online, activity=None)
        await interaction.followup.send("I'm awake now!", ephemeral=True)


    @app_commands.command(name="wake", description="Wake the bot up")
    async def wake(self, interaction: discord.Interaction):
        self.is_sleeping = False
        await self.bot.change_presence(status=discord.Status.online, activity=None)
        await interaction.response.send_message("I'm awake now!", ephemeral=True)

class MessageHandlerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        sleep_cog = self.bot.get_cog("SleepCog")
        if sleep_cog and sleep_cog.is_sleeping:
            return

        try:
            if message.author == self.bot.user:
                return

            if message.id in self.bot.processed_messages:
                return
            self.bot.processed_messages.append(message.id)

            log(f"[INCOMING][#{message.channel}] {message.author}: {message.content}", Fore.CYAN)

            if not message.guild:
                log(f"[DM] Ignoring DM from {message.author}", Fore.YELLOW)
                return

            perms = message.channel.permissions_for(message.guild.me)
            if not (perms.send_messages and perms.read_messages):
                return

            history = self.bot.conversation_history.get(message.channel.id, [])
            history.append({"author": str(message.author), "content": message.content})
            if len(history) > 10:
                history = history[-10:]
            self.bot.conversation_history[message.channel.id] = history

            is_direct_reply = message.reference and message.reference.resolved and message.reference.resolved.author == self.bot.user
            is_bot_mentioned = self.bot.user in message.mentions or "blevitron" in message.content.lower()

            if is_direct_reply or is_bot_mentioned:
                should_reply = True
            else:
                try:
                    should_reply = await should_bot_reply(message, history)
                except Exception as e:
                    log(f"[ERROR] Failed to determine if bot should reply: {e}", Fore.RED)
                    should_reply = False

            if should_reply and perms.send_messages:
                async with message.channel.typing():
                    try:
                        prompt = (
                            f"Recent chat history:\n{history}\n\n"
                            f"User: {message.content}"
                        )
                        response = await get_llm_response(prompt, history=history, user_id=message.author.id)
                        response = replace_with_mentions(response)
                        log(f"[OUTGOING][#{message.channel}] {self.bot.user}: {response}", Fore.GREEN)
                        await message.channel.send(response)

                        history.append({"author": str(self.bot.user), "content": response})
                        self.bot.conversation_history[message.channel.id] = history
                    except Exception as e:
                        log(f"[ERROR] Failed to generate or send response: {e}", Fore.RED)
        except Exception as e:
            log(f"[ERROR] Unexpected error in on_message: {e}", Fore.RED)

async def setup(bot):
    await bot.add_cog(SleepCog(bot))
    await bot.add_cog(MessageHandlerCog(bot))
