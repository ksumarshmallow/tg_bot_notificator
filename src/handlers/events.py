import re
import logging
from datetime import datetime, timedelta
import dateparser
from telegram import Update
from telegram.ext import ContextTypes

from src.database import (add_event, 
                          get_events, 
                          delete_event, 
                          get_event_id)

async def add_event_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите событие в формате: ДД.ММ.ГГГГ ЧЧ:ММ Описание")

async def handle_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    logging.debug(f"Received message: {text}")
    event_format = r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}) (.+)"
    match = re.match(event_format, text)
    if not match:
        await update.message.reply_text("❌ Ошибка! Введите в формате: ДД.ММ.ГГГГ ЧЧ:ММ Описание")
        return

    date_str = f"{match.group(3)}-{match.group(2)}-{match.group(1)}"
    time_str = f"{match.group(4)}:{match.group(5)}"
    description = match.group(6)

    await add_event(context.bot_data['db_conn'], update.effective_user.id, date_str, time_str, description)
    await update.message.reply_text("✅ Событие добавлено!")

async def show_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # По умолчанию - события на сегодня
    date = datetime.now().strftime("%Y-%m-%d")
    if context.args:
        user_date = " ".join(context.args)
        parsed_date = dateparser.parse(user_date, settings={'RETURN_AS_TIMEZONE_AWARE': False})
        if parsed_date:
            date = parsed_date.strftime("%Y-%m-%d")
        else:
            await update.message.reply_text(
                "❌ Ошибка! Не удалось распознать дату. Введите дату в формате ДД.ММ.ГГГГ или название месяца."
            )
            return

    events_list = await get_events(context.bot_data['db_conn'], update.effective_user.id, date)
    if events_list:
        text = "\n".join([f"⏰ {time} - {desc}" for _, time, desc in events_list])
    else:
        text = f"На {date} нет событий."
    await update.message.reply_text(text)

async def delete_event_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Ошибка! Для удаления события укажите дату и время в формате: /delete ДД.ММ.ГГГГ ЧЧ:ММ"
        )
        return

    date_time_str = " ".join(context.args)
    parsed_date = dateparser.parse(date_time_str, settings={'RETURN_AS_TIMEZONE_AWARE': False})
    if not parsed_date:
        await update.message.reply_text(
            "❌ Ошибка! Не удалось распознать дату и время. Введите дату в формате ДД.ММ.ГГГГ ЧЧ:ММ."
        )
        return

    date = parsed_date.strftime("%Y-%m-%d")
    time = parsed_date.strftime("%H:%M")
    rows = delete_event(context.bot_data['db_conn'], update.effective_user.id, date, time)
    if rows > 0:
        await update.message.reply_text(f"✅ Событие на {date} в {time} удалено!")
    else:
        await update.message.reply_text(f"❌ Событие на {date} в {time} не найдено.")

async def get_event_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "❌ Ошибка! Укажите дату и время в формате: /get_id ДД.ММ.ГГГГ ЧЧ:ММ"
        )
        return

    date_time_str = " ".join(context.args)
    parsed_date = dateparser.parse(date_time_str, settings={'RETURN_AS_TIMEZONE_AWARE': False})
    if not parsed_date:
        await update.message.reply_text(
            "❌ Ошибка! Не удалось распознать дату и время. Попробуйте в формате: ДД.ММ.ГГГГ ЧЧ:ММ."
        )
        return

    date = parsed_date.strftime("%Y-%m-%d")
    time = parsed_date.strftime("%H:%M")
    event = get_event_id(context.bot_data['db_conn'], update.effective_user.id, date, time)
    if event:
        await update.message.reply_text(f"✅ ID события на {date} в {time}: {event[0]}")
    else:
        await update.message.reply_text(f"❌ Событие на {date} в {time} не найдено.")

async def send_tomorrow_notifications(context: ContextTypes.DEFAULT_TYPE):
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    conn = context.bot_data['db_conn']
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, time, description FROM events WHERE date = ?", (tomorrow,))
    events = cursor.fetchall()
    for user_id, time, description in events:
        await context.bot.send_message(user_id, f"🔔 Напоминание! Завтра в {time}: {description}")
