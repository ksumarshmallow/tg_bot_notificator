import re
import logging
import requests
import aiohttp
from dataclasses import dataclass
from datetime import datetime, timedelta
from dateparser.search import search_dates

from abc import ABC, abstractmethod
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def parse_datetime(text):
    """
    Парсит дату из текста с помощью dateparser.
    Если в тексте есть время, возвращает 'YYYY-MM-DD HH:MM', иначе 'YYYY-MM-DD'
    """
    parsed_date = search_dates(text, languages=["ru"])
    pattern_time = re.search(r'\d\d:\d\d', text)

    if not parsed_date:
        return None
    
    date = parsed_date[0][1].strftime("%Y-%m-%d %H:%M") if pattern_time is not None \
            else parsed_date[0][1].strftime("%Y-%m-%d")
    
    return date


def event_or_todo(date):
    # 1 - todo; 0 - event
    return bool(re.search(r'\d\d:\d\d', date))


class BotState(ABC):
    @abstractmethod
    async def handle(self, bot, update, context):
        """
        Основной метод, который обрабатывает сообщение в данном состоянии.
        :param bot: экземпляр основного класса бота (например, TelegramCalendarBot)
        :param update: объект Update
        :param context: CallbackContext
        """
        pass


# Состояние: ожидание ввода даты для создания события
class AwaitingEventDateState(BotState):
    async def handle(self, bot, update, context):
        user_id = update.effective_user.id
        text = update.message.text
        date = parse_datetime(text)
        if date is None:
            logger.warning(f"User {user_id} sent invalid date: {text}")
            await update.message.reply_text("Не понял дату 🥲. Попробуй ещё раз")
            return
        context.user_data["temp_date"] = date
        # Переходим к следующему состоянию – ввод названия события
        context.user_data["state"] = "awaiting_event_name"
        await update.message.reply_text("✍️ Теперь напиши название события")


# Состояние: ожидание ввода названия события
class AwaitingEventNameState(BotState):
    async def handle(self, bot, update, context):
        user_id = update.effective_user.id
        event_name = update.message.text
        temp_date = context.user_data.get("temp_date")
        if not temp_date:
            await update.message.reply_text("Дата потерялась 🥲, попробуй снова")
            return

        # Формируем запрос на добавление события
        url = f"{bot.backend_url}/todos" if event_or_todo(temp_date) else f"{bot.backend_url}/events"
        payload = {"user_id": user_id, "name": event_name, "date": temp_date}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status in {200, 201}:
                    logger.info(f"User {user_id} successfully added event: {event_name} on {temp_date}")
                    await update.message.reply_text(f"Событие '{event_name}' записано на {temp_date}!")
                else:
                    logger.error(f"User {user_id} failed to add event: {event_name} ({temp_date}). Status: {resp.status}")
                    await update.message.reply_text("Ошибка при добавлении события 🛠️")

        # Сбрасываем состояние
        context.user_data["state"] = None
        context.user_data.pop("temp_date", None)


# Состояние: ожидание ввода даты для удаления события/заметки
class AwaitingDeleteDateState(BotState):
    async def handle(self, bot, update, context):
        user_id = update.effective_user.id
        text = update.message.text
        date = parse_datetime(text)
        if date is None:
            logger.warning(f"User {user_id} sent invalid date: {text}")
            await update.message.reply_text("Не понял дату 🥲. Попробуй ещё раз")
            return
        context.user_data["temp_date"] = date

        # Получаем события на данную дату через backend API
        response = await bot.fetch_events_by_date(user_id, date)
        if response is None or not response:
            await update.message.reply_text("На этот день ничего нет 😌")
            # Сбрасываем состояние
            context.user_data["state"] = None
            return

        # Сохраняем список событий для выбора пользователем
        events_mapping = {str(i + 1): event["name"] for i, event in enumerate(response)}
        context.user_data["delete_events"] = events_mapping
        events_list = "\n".join(f"{i+1}. {name}" for i, name in events_mapping.items())
        await update.message.reply_text(f"📅 События на {date}:\nВыбери номер события для удаления:\n{events_list}")

        context.user_data["state"] = "awaiting_delete_choice"