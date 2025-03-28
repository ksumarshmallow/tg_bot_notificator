import os
import asyncio
from dotenv import load_dotenv
from src.bot import TelegramCalendarBot

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    bot_instance = TelegramCalendarBot(token=TOKEN)
    asyncio.run(bot_instance.start())
