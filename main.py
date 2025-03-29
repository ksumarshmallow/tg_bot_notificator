import os
import asyncio
import threading
from dotenv import load_dotenv
from bot.bot import TelegramCalendarBot
from backend.routes import app

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

def run_bot():
    bot_instance = TelegramCalendarBot(token=TOKEN)
    bot_instance.run()

def run_flask():
    app.run(debug=True, use_reloader=False, port=5001)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    loop.create_task(run_bot())
    loop.run_forever()