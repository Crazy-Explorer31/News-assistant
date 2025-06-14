from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from news_assistant_handlers import button_handler, handle_text, start
from news_classifier_load import identity_tokenizer

print("Loading NewsAssistant_bot...")

# Создание приложения
app = (
    ApplicationBuilder().token("7814824438:AAFGsjmeb19DuZayWFgaMqFndy17Eh-AA1A").build()
)

# Добавление обработчиков команд и текстовых сообщений
app.add_handler(CommandHandler("help", help))  # Обработчик для команды /help
app.add_handler(CommandHandler("start", start))  # Обработчик для команды /start
app.add_handler(
    MessageHandler(
        filters.TEXT
        & ~filters.COMMAND
        & (
            filters.Regex("^Добавить каналы$")
            | filters.Regex("^Удалить каналы$")
            | filters.Regex("^Просмотреть каналы$")
            | filters.Regex("^Получить новости$")
            | filters.Regex("^Изменить новостные категории$")
            | filters.Regex("^Изменить число считываемых новостей$")
        ),
        button_handler,
    )
)  # Обработчик для кнопок
app.add_handler(
    MessageHandler(filters.TEXT, handle_text)
)  # Обработчик для текстовых сообщений

print("Loaded!")
# Запуск бота
app.run_polling()
