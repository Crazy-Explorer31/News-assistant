import telegram
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes

from manage_user_data import *
from news_filter import get_filtered_news
from news_reader import channel_exists, get_news, get_pretty_news

# Статус ---> эмодзи
status_emoji = {True: "✅", False: "❌"}

# Статус_строка ---> статус_булеан
status_to_bool = {"1": True, "0": False}


# Функция для создания начальной клавиатуры
def get_start_keyboard():
    keyboard = [
        ["Добавить каналы", "Удалить каналы"],
        ["Просмотреть каналы", "Получить новости", "Изменить новостные категории"],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_categories_keyboard(user_id: str):
    choosen_categories = get_user_categories(user_id)
    choosen_categories_info = list(choosen_categories.items())
    choosen_categories_info = [
        (category, status_to_bool[is_choosen])
        for category, is_choosen in choosen_categories_info
    ]
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
    user_id = str(update.message.from_user.id)
    channels = get_user_channels(user_id)

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
    user_id = str(update.message.from_user.id)
    sure_user_registration(user_id)
    channels = get_user_channels(user_id)
    choosen_categories = get_user_categories(user_id)

    news = await get_news(channels)  # Получаем новости
    if len(news) == 0:
        await update.message.reply_text(
            "Новостей не нашлось",
            reply_markup=get_start_keyboard(),
            disable_web_page_preview=True,
        )
        return
    news = get_filtered_news(news, categories, choosen_categories)
    if len(news) == 0:
        await update.message.reply_text(
            "Подходящих новостей не нашлось",
            reply_markup=get_start_keyboard(),
            disable_web_page_preview=True,
        )
        return
    news = get_pretty_news(news)
    # news = get_pretty_news_parse_mode(news)
    for item in news:
        if item[0] == "" or item[1] == "":
            continue

        await update.message.reply_text(
            item[0],
            reply_markup=get_start_keyboard(),
            disable_web_page_preview=True,
            parse_mode="Markdown",
        )
        try:
            await update.message.reply_text(
                item[1],
                reply_markup=get_start_keyboard(),
                disable_web_page_preview=True,
                parse_mode="Markdown",
            )
        except telegram.error.BadRequest:
            await update.message.reply_text(
                item[1],
                reply_markup=get_start_keyboard(),
                disable_web_page_preview=True,
                parse_mode="HTML",
            )


# Обработчик кнопки "Изменить новостные категории"
async def change_current_categories(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user_id = str(update.message.from_user.id)
    sure_user_registration(user_id)

    await update.message.reply_text(
        "Выберите нужные новостные категории:",
        reply_markup=get_categories_keyboard(user_id),
    )
    context.user_data["action"] = "categories_change"  # Сохраняем действие


# Обработчик текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.message.from_user.id)
    action = context.user_data.get("action")
    if action == "add":
        new_channels = update.message.text.split()

        good_channels = [
            new_channel
            for new_channel in new_channels
            if await channel_exists(new_channel)
        ]
        bad_channels = [
            new_channel
            for new_channel in new_channels
            if not (await channel_exists(new_channel))
        ]
        if bad_channels:
            await update.message.reply_text(
                f'Каналы не существуют: {", ".join(bad_channels)}',
                reply_markup=get_start_keyboard(),
            )
        if good_channels:
            add_user_channels(user_id, set(good_channels))
            await update.message.reply_text(
                f'Каналы добавлены: {", ".join(good_channels)}',
                reply_markup=get_start_keyboard(),
            )
        if not good_channels and not bad_channels:
            await update.message.reply_text(
                "Вы не ввели каналы.", reply_markup=get_start_keyboard()
            )
        context.user_data["action"] = None  # Сбрасываем действие
    elif action == "remove":
        channels = get_user_channels(user_id)
        channels_to_remove = update.message.text.split()
        removed_channels = [
            channel for channel in channels_to_remove if channel in channels
        ]
        if removed_channels:
            remove_user_channels(user_id, set(removed_channels))
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

        elif change_command in categories.keys():
            changed_status_msg = change_user_categories(user_id, change_command)
            await update.message.reply_text(
                f"Категория *{change_command}* {changed_status_msg}",
                parse_mode="Markdown",
                reply_markup=get_categories_keyboard(user_id),
            )

        else:
            await update.message.reply_text(
                "Выберите новостные категории из меню!",
                reply_markup=get_categories_keyboard(user_id),
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
