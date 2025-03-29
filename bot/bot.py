import logging
import aiohttp
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from dataclasses import dataclass
from bot.states import (
    AwaitingDateState,
    AwaitingNameState,
    AwaitingDeleteDateState,
    AwaitingDeleteChoiceState,
)

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

STATE_HANDLERS = {
    "awaiting_event_date": AwaitingDateState(),
    "awaiting_todo_date": AwaitingDateState(),
    "awaiting_event_name": AwaitingNameState(),
    "awaiting_todo_name": AwaitingNameState(),
    "awaiting_delete_date": AwaitingDeleteDateState(),
    "awaiting_delete_choice": AwaitingDeleteChoiceState(),
}

@dataclass
class TelegramCalendarBot:
    token: str

    def __post_init__(self):
        self.start_message = (
            "Привет! Я твой календарь-бот 📅.\n"
            "Используй кнопки для управления событиями."
        )
        self.buttons = {
            "Добавить событие": self.add_event,
            "Добавить заметку": self.add_todo,
            "Удалить событие или заметку": self.delete_event,
            "Открыть календарь": self.open_calendar,
        }
        keyboard = [[btn] for btn in self.buttons]
        self.reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        self.backend_url = "http://127.0.0.1:5001"

    async def start(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} started bot")
        await update.message.reply_text(self.start_message, reply_markup=self.reply_markup)

    async def add_event(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} wants to add an event")
        # начальное состояние для добавления события
        context.user_data["state"] = "awaiting_event_date"
        context.user_data["type"] = "event"
        await update.message.reply_text("Укажи дату и время события 📅 (например, 'завтра в 15:00')")

    async def add_todo(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} wants to add a todo")
        context.user_data["state"] = "awaiting_todo_date"
        context.user_data["type"] = "todo"
        # Для простоты оставим этот путь без реализации, можно сделать аналогично add_event
        await update.message.reply_text("Укажи дату события 📅 (например, 'завтра')")

    async def delete_event(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} wants to delete an event")
        # Устанавливаем состояние для удаления
        context.user_data["state"] = "awaiting_delete_date"
        await update.message.reply_text("Укажи дату события, которое хочешь удалить (например, 'завтра')")

    async def open_calendar(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} opened calendar.")
        await update.message.reply_text("Здесь будет твой календарь. Пока прото представь его :) У тебя же хорошее воображение?")

    async def fetch_events_by_date(self, user_id, date):
        url = f"{self.backend_url}/events/by_date"
        payload = {"user_id": user_id, "date": date}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, json=payload) as resp:
                if resp.status in {200, 201}:
                    return await resp.json()
                else:
                    return None

    async def handle_text(self, update: Update, context: CallbackContext):
        text = update.message.text
        user_id = update.effective_user.id

        if text in self.buttons:
            return await self.buttons[text](update, context)

        # есои установлено состояние, делегируем обработку соответствующему классу
        current_state = context.user_data.get("state")
        if current_state in STATE_HANDLERS:
            handler = STATE_HANDLERS[current_state]
            await handler.handle(self, update, context)
        else:
            logger.warning(f"User {user_id} sent unrecognized text: {text}")
            await update.message.reply_text("Не понимаю ничего... 🥲 Используй кнопки или команды.")

    def run(self):
        app = Application.builder().token(self.token).build()
        
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("addevent", self.add_event))
        app.add_handler(CommandHandler("addtodo", self.add_todo))
        app.add_handler(CommandHandler("delete", self.delete_event))
        
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        
        logger.info("Bot is started...")
        
        app.run_polling(close_loop=False)

