from dotenv import load_dotenv
import os

from src.bot import TelegramCalendarBot


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if __name__ == "__main__":
    bot_instance = TelegramCalendarBot(token=TOKEN)
    bot_instance.run()
