import asyncio
import logging
import sqlite3
import os
from dataclasses import dataclass
from aiogram import Bot, Dispatcher, types, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta


@dataclass
class TelegramCalendarBot:
    token: str
    db_path: str = "calendar.db"
    bot: Bot = None
    dp: Dispatcher = None
    router: Router = None
    conn: sqlite3.Connection = None
    cursor: sqlite3.Cursor = None
    scheduler: AsyncIOScheduler = None

    def __post_init__(self):
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        self.router = Router()
        self.dp.include_router(self.router)
        logging.basicConfig(level=logging.INFO)
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                               id INTEGER PRIMARY KEY AUTOINCREMENT,
                               user_id INTEGER,
                               date TEXT,
                               time TEXT,
                               description TEXT)''')
        self.conn.commit()
        
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.send_tomorrow_notifications, "cron", hour=20, minute=0)
        self.scheduler.start()
        
        # Регистрация обработчиков
        self.router.message.register(self.add_command, commands=['add'])
        self.router.message.register(self.handle_event)
        self.router.message.register(self.show_today_events, commands=['day'])

    async def add_event(self, user_id, date, time, description):
        self.cursor.execute("INSERT INTO events (user_id, date, time, description) VALUES (?, ?, ?, ?)",
                            (user_id, date, time, description))
        self.conn.commit()

    async def get_events(self, user_id, date):
        self.cursor.execute("SELECT time, description FROM events WHERE user_id = ? AND date = ?", (user_id, date))
        return self.cursor.fetchall()

    async def add_command(self, message: types.Message):
        await message.reply("Введите событие в формате: ДД.ММ.ГГГГ ЧЧ:ММ Описание")

    async def handle_event(self, message: types.Message):
        try:
            data = message.text.split(" ", 2)
            date = datetime.strptime(data[0], "%d.%m.%Y").strftime("%Y-%m-%d")
            time = data[1]
            description = data[2]
            await self.add_event(message.from_user.id, date, time, description)
            await message.reply("✅ Событие добавлено!")
        except:
            await message.reply("❌ Ошибка! Введите в формате: ДД.ММ.ГГГГ ЧЧ:ММ Описание")

    async def show_today_events(self, message: types.Message):
        date = datetime.now().strftime("%Y-%m-%d")
        events = await self.get_events(message.from_user.id, date)
        if events:
            text = "\n".join([f"⏰ {time} - {desc}" for time, desc in events])
        else:
            text = "Нет событий на сегодня."
        await message.reply(text)

    async def send_tomorrow_notifications(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.cursor.execute("SELECT user_id, time, description FROM events WHERE date = ?", (tomorrow,))
        events = self.cursor.fetchall()
        for user_id, time, description in events:
            await self.bot.send_message(user_id, f"🔔 Напоминание! Завтра в {time}: {description}")

    async def start(self):
        await self.dp.start_polling(self.bot)