from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from news_reader import get_news

# Список для хранения каналов
channels = []


# Обработчик команды /add_channels
async def add_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        # Получаем каналы из аргументов команды
        new_channels = context.args
        channels.extend(new_channels)  # Добавляем новые каналы в список
        await update.message.reply_text(f'Каналы добавлены: {", ".join(new_channels)}')
    else:
        await update.message.reply_text(
            "Пожалуйста, укажите каналы для добавления через пробел."
        )


# Обработчик команды /remove_channels
async def remove_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.args:
        # Получаем каналы из аргументов команды
        channels_to_remove = context.args
        for channel in channels_to_remove:
            if channel in channels:
                channels.remove(channel)  # Удаляем канал из списка
        await update.message.reply_text(
            f'Каналы удалены: {", ".join(channels_to_remove)}'
        )
    else:
        await update.message.reply_text(
            "Пожалуйста, укажите каналы для удаления через пробел."
        )


# Обработчик команды /view_channels
async def view_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if channels:
        await update.message.reply_text(
            f'Текущий список каналов: {", ".join(channels)}'
        )
    else:
        await update.message.reply_text("Список каналов пуст.")


async def get_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    news = await get_news(channels)  # Получаем новости
    await update.message.reply_text(news)


# Создание приложения
app = (
    ApplicationBuilder().token("7814824438:AAFGsjmeb19DuZayWFgaMqFndy17Eh-AA1A").build()
)

# Добавление обработчиков команд
app.add_handler(CommandHandler("add_channels", add_channels))
app.add_handler(CommandHandler("remove_channels", remove_channels))
app.add_handler(CommandHandler("view_channels", view_channels))
app.add_handler(CommandHandler("get_news", get_news_command))

# Запуск бота
app.run_polling()
