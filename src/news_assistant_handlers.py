from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from news_filter import get_filtered_news
from news_reader import get_joined_news, get_news

# Список для хранения каналов
channels = []


# Функция для создания клавиатуры
def get_keyboard():
    keyboard = [
        ["Добавить каналы", "Удалить каналы"],
        ["Просмотреть каналы", "Получить новости", "Изменить новостные категории"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Добро пожаловать! Выберите команду:", reply_markup=get_keyboard()
    )


# Обработчик кнопки "Добавить каналы"
async def add_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Введите каналы через пробел (например, если интересен @pitlive, то напишите pitlive):",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data["action"] = "add"  # Сохраняем действие


# Обработчик кнопки "Удалить каналы"
async def remove_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Введите каналы для удаления через пробел (например, если удаляете @pitlive, то напишите pitlive):",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data["action"] = "remove"  # Сохраняем действие


# Обработчик кнопки "Просмотреть каналы"
async def view_channels(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if channels:
        await update.message.reply_text(
            f'Текущий список каналов: {", ".join(channels)}'
        )
    else:
        await update.message.reply_text("Список каналов пуст.")


# Обработчик кнопки "Получить новости"
async def get_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    news = await get_news(channels)  # Получаем новости
    news = get_filtered_news(news)
    news = get_joined_news(news)
    await update.message.reply_text(news, disable_web_page_preview=True)


# Обработчик текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    action = context.user_data.get("action")
    if action == "add":
        new_channels = update.message.text.split()
        if new_channels:
            channels.extend(new_channels)
            await update.message.reply_text(
                f'Каналы добавлены: {", ".join(new_channels)}',
                reply_markup=get_keyboard(),
            )
        else:
            await update.message.reply_text(
                "Вы не ввели каналы.", reply_markup=get_keyboard()
            )
        context.user_data["action"] = None  # Сбрасываем действие
    elif action == "remove":
        channels_to_remove = update.message.text.split()
        removed_channels = [
            channel for channel in channels_to_remove if channel in channels
        ]
        for channel in removed_channels:
            channels.remove(channel)
        if removed_channels:
            await update.message.reply_text(
                f'Каналы удалены: {", ".join(removed_channels)}',
                reply_markup=get_keyboard(),
            )
        else:
            await update.message.reply_text(
                "Каналы не найдены для удаления.", reply_markup=get_keyboard()
            )
        context.user_data["action"] = None  # Сбрасываем действие
    else:
        await update.message.reply_text("Пожалуйста, выберите команду из меню.")


# Обработчик текстовых сообщений для кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if text == "Добавить каналы":
        await add_channels(update, context)
    elif text == "Удалить каналы":
        await remove_channels(update, context)
    elif text == "Просмотреть каналы":
        await view_channels(update, context)
    elif text == "Получить новости":
        await get_news_command(update, context)
