import json

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from news_filter import get_filtered_news
from news_reader import get_news, get_pretty_news

# Текущие каналы
channels = []

# Категории ---> коды
with open("include/news_categories.json", "r", encoding="utf-8") as file:
    categories = json.load(file)

# Категории ---> выбраны ли
choosen_categories = {
    "Общество / Россия": True,
    "Экономика": True,
    "Силовые структуры": True,
    "Бывший СССР": True,
    "Спорт": True,
    "Здоровье": True,
    "Строительство": True,
    "Туризм": True,
}

# Статус ---> эмодзи
status_emoji = {True: "✅", False: "❌"}


# Функция для создания начальной клавиатуры
def get_start_keyboard():
    keyboard = [
        ["Добавить каналы", "Удалить каналы"],
        ["Просмотреть каналы", "Получить новости", "Изменить новостные категории"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_categories_keyboard():
    choosen_categories_info = list(choosen_categories.items())
    keyboard = [
        [
            status_emoji[is_choosen] + " " + category
            for category, is_choosen in choosen_categories_info[:2]
        ]
    ]
    keyboard += [
        [
            status_emoji[is_choosen] + " " + category
            for category, is_choosen in choosen_categories_info[2:5]
        ]
    ]
    keyboard += [
        [
            status_emoji[is_choosen] + " " + category
            for category, is_choosen in choosen_categories_info[5:]
        ]
    ]
    keyboard += [["🔙 Вернуться"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Обработчик команды /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Вас приветствует новоствой ассистент!\n"
        "Здесь Вы можете читать новости из разных телеграм каналов, при этом:"
        "- выбирая, какие каналы интересны Вам"
        "- выбирая, какие новостные категории интересны Вам."
    )


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Добро пожаловать! Выберите команду:", reply_markup=get_start_keyboard()
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
            f'Текущий список каналов: {", ".join(channels)}',
            reply_markup=get_start_keyboard(),
        )
    else:
        await update.message.reply_text(
            "Список каналов пуст.", reply_markup=get_start_keyboard()
        )


# Обработчик кнопки "Получить новости"
async def get_news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    news = await get_news(channels)  # Получаем новости
    if len(news) == 0:
        await update.message.reply_text(
            "Подходящих новостей не нашлось",
            reply_markup=get_start_keyboard(),
            disable_web_page_preview=True,
        )
        return
    news = get_filtered_news(news, categories, choosen_categories)
    news = get_pretty_news(news)
    for item in news:
        await update.message.reply_text(
            item,
            reply_markup=get_start_keyboard(),
            disable_web_page_preview=True,
            parse_mode="Markdown",
        )


# Обработчик кнопки "Изменить новостные категории"
async def change_current_categories(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    await update.message.reply_text(
        "Выберите нужные новостные категории:",
        reply_markup=get_categories_keyboard(),
    )
    context.user_data["action"] = "categories_change"  # Сохраняем действие


# Обработчик текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    action = context.user_data.get("action")
    if action == "add":
        new_channels = update.message.text.split()
        if new_channels:
            channels.extend(new_channels)
            await update.message.reply_text(
                f'Каналы добавлены: {", ".join(new_channels)}',
                reply_markup=get_start_keyboard(),
            )
        else:
            await update.message.reply_text(
                "Вы не ввели каналы.", reply_markup=get_start_keyboard()
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
                reply_markup=get_start_keyboard(),
            )
        else:
            await update.message.reply_text(
                "Каналы не найдены для удаления.", reply_markup=get_start_keyboard()
            )
        context.user_data["action"] = None  # Сбрасываем действие
    elif action == "categories_change":
        change_command = update.message.text.split()[1:]
        change_command = " ".join(change_command)

        if change_command == "Вернуться":
            context.user_data["action"] = None  # Сбрасываем действие
            await update.message.reply_text(
                "Пожалуйста, выберите команду из меню.",
                reply_markup=get_start_keyboard(),
            )

        elif change_command in choosen_categories.keys():
            changed_status = not choosen_categories[change_command]
            choosen_categories[change_command] = changed_status
            changed_status_msg = "добавлена" if changed_status else "удалена"
            await update.message.reply_text(
                f"Категория *{change_command}* {changed_status_msg}",
                parse_mode="Markdown",
                reply_markup=get_categories_keyboard(),
            )

        else:
            await update.message.reply_text(
                "Выберите новостные категории из меню!",
                reply_markup=get_categories_keyboard(),
            )
            print(change_command, "failed")  # TODO: remove

    else:
        await update.message.reply_text(
            "Пожалуйста, выберите команду из меню.", reply_markup=get_start_keyboard()
        )


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
    elif text == "Изменить новостные категории":
        await change_current_categories(update, context)
