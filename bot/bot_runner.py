import os
import asyncio
from dotenv import load_dotenv
from bot.bot import TelegramCalendarBot

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot_instance = TelegramCalendarBot(token=TOKEN)
    loop.create_task(bot_instance.run())

    loop.run_forever()
