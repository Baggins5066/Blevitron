import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")

config = Config()
