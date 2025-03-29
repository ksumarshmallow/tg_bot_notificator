import re
import logging
import requests
import aiohttp
from dataclasses import dataclass
from datetime import datetime, timedelta
from dateparser.search import search_dates

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

#TODO: deadlines
#TODO: event from start_date to end_date (deadline)
#TODO: add links to events (zoom etc), any comments

@dataclass
class TelegramCalendarBot:
    token: str

    def __post_init__(self):
        self.start_message = (
            "Привет, дорогой пользователь! Я - твой календарь-бот 📅\n\nМоя задача - помочь тебе планировать события и вовремя напомнить о них 😊"
            "\n\nА теперь время знакомиться! Вот мои команды:\n"
            "▫️ /add - добавить новое событие\n"
            "▫️ /help - показать этот список команд\n\n"
            "Если возникнут проблемы – пиши моему создателю: @ksu_marshmallow 🐱\n\n"
            "Пора начинать Трудовую Буржуазную Жизнь! 💵"
        )

        self.buttons = {
            "Добавить событие": self.add_event,
            "Добавить заметку": self.add_todo,
            "Удалить событие или заметку": self.delete_event,
            "Открыть календарь": self.open_calendar,
        }

        keyboard = [[btn] for btn in self.buttons]

        self.reply_markup = ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )

        self.backend_url = "http://127.0.0.1:5001"

    async def start(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} started bot")
        await update.message.reply_text(self.start_message, reply_markup=self.reply_markup)

    async def add_event(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} wants to add an event")
        context.user_data["state"] = "awaiting_event_date"
        await update.message.reply_text("Укажи дату и время события 📅 (например, 'завтра в 15:00' или формат 'YYYY-MM-DD HH:MM')")
    
    async def add_todo(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} wants to add a to-do")
        context.user_data["state"] = "awaiting_todo_date"
        await update.message.reply_text("Укажи дату заметки 📅 (например, 'завтра' или формат 'YYYY-MM-DD')")
    
    async def delete_event(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} wants to delete event")
        context.user_data["state"] = "awaiting_delete_date"
        await update.message.reply_text("Укажи дату события, которое хочешь удалить (например, 'завтра' или формат 'YYYY-MM-DD')")

    async def open_calendar(self, update: Update, context: CallbackContext):
        logger.info(f"User {update.effective_user.id} opened calendar.")
        await update.message.reply_text("📅 Здесь будет твой календарь. Пока просто представь его))")
    
    def _parse_datetime(self, text):
        parsed_date = search_dates(text, languages=["ru"])
        pattern_time = re.search(r'\d\d:\d\d', text)

        if not parsed_date:
            return None
        
        date = parsed_date[0][1].strftime("%Y-%m-%d %H:%M") if pattern_time is not None else parsed_date[0][1].strftime("%Y-%m-%d")
        return date

    async def handle_text(self, update: Update, context: CallbackContext):
        text = update.message.text
        user_id = update.effective_user.id
        state = context.user_data.get("state")

        if text in self.buttons:
            return await self.buttons[text](update, context)
        
        # 1. Парсим дату и просим событие
        if state == "awaiting_event_date" or state == "awaiting_todo_date":
            date = self._parse_datetime(text)
            if date is None:
                logger.warning(f"User {user_id} sent invalid date: {text}")
                return await update.message.reply_text("Не понял дату 🥲. Попробуй еще раз")
            context.user_data["temp_date"] = date
        
            if state == "awaiting_event_date":
                context.user_data["state"] = "awaiting_event_name"
                await update.message.reply_text("✍️ Теперь напиши твое событие")
            else:
                context.user_data["state"] = "awaiting_todo_name"
                await update.message.reply_text("✍️ Теперь напиши твое дело для TODO-шки")
        
        # 2. Добавляем событие
        elif state=="awaiting_event_name" or state=="awaiting_todo_name":
            event_name = text
            event_date = context.user_data.pop("temp_date", None)

            if not event_date:
                return await update.message.reply_text("Дата потерялась 🥲, попробуй снова")
            
            # make URL and data for query
            url = f"{self.backend_url}/events" if state=="awaiting_event_name" else f"{self.backend_url}/todos"
            logger.info(url)
            payload = {"user_id": user_id, "name": event_name, "date": event_date}

            # assynchrnucally send POST-query on server
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 201:
                        logger.info(f"User {user_id} successfully added {'event' if state=='awaiting_event_name' else 'todo'}: {event_name} ({event_date})")
                    else:
                        logger.error(f"User {user_id} failed to add {'event' if state=='awaiting_event_name' else 'todo'}: {event_name} ({event_date}). Status: {resp.status}")
            
            logger.info(f"User {user_id} added {state.split('_')[1]}: {event_name} ({event_date})")
            context.user_data["state"] = None
            await update.message.reply_text(f"Событие '{event_name}' записано на {event_date}!")
        
        # 3. Удалить событие: парсим дату
        elif state == "awaiting_delete_date":
            date = self._parse_datetime(text)
            if date is None:
                logger.warning(f"User {user_id} sent invalid date: {text}")
                return await update.message.reply_text("Не понял дату 🥲. Попробуй еще раз")

            context.user_data["temp_date"] = date

            response = requests.get(f"{self.backend_url}/events/by_date", json={"user_id": user_id, "date": date})

            if response.status_code != 200:
                return await update.message.reply_text("Ошибка сервера 🛠️")

            events = response.json()

            if not events:
                return await update.message.reply_text("На этот день ничего нет 😌")

            # Сохраняем список событий в user_data
            context.user_data["delete_events"] = {str(i+1): event["name"] for i, event in enumerate(events)}

            events_list = "\n".join(f"{i+1}. {event['name']}" for i, event in enumerate(events))
            await update.message.reply_text(f"📅 События на {date}:\nВыбери номер события для удаления:\n{events_list}")

            context.user_data["state"] = "awaiting_delete_event"
        
        # 4. Удаление события: пользователь выбирает событие
        elif state == "awaiting_delete_event":
            event_index = text.strip()
            event_name = context.user_data.get("delete_events", {}).get(event_index)

            if not event_name:
                return await update.message.reply_text("Неверный номер! Введи цифру из списка 🧐")

            date = context.user_data["temp_date"]

            # Отправляем запрос на удаление
            url = f"{self.backend_url}/events/delete"
            payload = {"user_id": user_id, "name": event_name, "date": date}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status in {200, 201}:
                        await update.message.reply_text(f"Событие '{event_name}' удалено!")
                    else:
                        await update.message.reply_text("Ошибка при удалении 🛠️")

            context.user_data["state"] = None
            context.user_data.pop("delete_events", None)
            context.user_data.pop("temp_date", None)


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