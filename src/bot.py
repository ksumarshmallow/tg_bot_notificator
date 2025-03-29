import logging
from datetime import datetime
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.database import init_db
from src.handlers.start import start_command, help_command
from src.handlers.events import (
    add_event_command,
    handle_event,
    show_events,
    delete_event_command,
    get_event_id_command,
    send_tomorrow_notifications,
)

logging.basicConfig(level=logging.DEBUG)

class TelegramCalendarBot:
    def __init__(self, token: str, db_path: str = "calendar.db"):
        self.token = token
        self.db_path = db_path
        self.db_conn = init_db(db_path)
        self.app = Application.builder().token(token).build()

        self.app.bot_data['db_conn'] = self.db_conn
        self.register_handlers()

    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", start_command))
        self.app.add_handler(CommandHandler("help", help_command))
        self.app.add_handler(CommandHandler("add", add_event_command))
        self.app.add_handler(CommandHandler("day", show_events))
        self.app.add_handler(CommandHandler("delete", delete_event_command))
        self.app.add_handler(CommandHandler("get_id", get_event_id_command))
        self.app.add_handler(MessageHandler(~filters.COMMAND, handle_event))

        job_queue = self.app.job_queue
        job_queue.run_daily(send_tomorrow_notifications, time=datetime.strptime("20:00", "%H:%M").time())

    def run(self):
        self.app.run_polling()
