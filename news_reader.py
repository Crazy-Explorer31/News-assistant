from telethon import TelegramClient # type: ignore

api_id = "27744421"
api_hash = "b76a43b4259bee6cb9899bcc9ca5d731"
client = TelegramClient("NewsReader", api_id, api_hash)

separator = "\n\n-----------------------------------------------------------------------------------------------\n\n"

async def get_news(channels) -> str:
    news = []
    await client.start()  # Запускаем клиента

    for channel in channels:
        try:
            async for message in client.iter_messages(
                channel, limit=2
            ):  # Получаем последнее сообщение
                news.append(f"{channel}: {message.text}")
        except Exception as e:
            news.append(f"Ошибка при получении новостей из {channel}: {str(e)}")

    await client.disconnect()  # Отключаем клиента
    return separator.join(news) if news else "Нет новостей."
