from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "Вот мои команды:\n\n"
        "▫️ /add - добавить новое событие\n"
        "▫️ /delete - удалить событие\n"
        "▫️ /day - показать события на сегодня или на любую дату (например, /day 28.03.2025)\n"
        "▫️ /get_id - получить ID события по дате и времени (например, /get_id 28.03.2025 14:30)\n"
        "▫️ /help - показать этот список команд\n\n"
        "События можно добавлять на любой день. Если не указывать дату, она считается сегодняшней.\n"
        "Если возникнут проблемы – пиши моему создателю: @ksu_marshmallow.\n\n"
        "Ну а теперь пора начинать Трудовую Буржуазную Жизнь! 💵"
    )
    start_message_full = (
        "Привет, дорогой пользователь! Я - твой календарь-бот. Моя задача — помочь тебе планировать события и напомнить о них 😊\n\n"
        "А теперь время знакомиться!\n" + help_message
    )
    await update.message.reply_text(start_message_full)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = (
        "Вот мои команды:\n\n"
        "▫️ /add - добавить новое событие\n"
        "▫️ /delete - удалить событие\n"
        "▫️ /day - показать события на сегодня или на любую дату (например, /day 28.03.2025)\n"
        "▫️ /get_id - получить ID события по дате и времени (например, /get_id 28.03.2025 14:30)\n"
        "▫️ /help - показать этот список команд\n\n"
        "События можно добавлять на любой день. Если не указывать дату, она считается сегодняшней.\n"
        "Если возникнут проблемы – пиши моему создателю: @ksu_marshmallow.\n\n"
        "Ну а теперь пора начинать Трудовую Буржуазную Жизнь! 💵"
    )
    await update.message.reply_text(help_message)
