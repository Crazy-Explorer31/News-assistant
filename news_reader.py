from telethon import TelegramClient # type: ignore
import sys

if len(sys.argv) != 3:
    print("Использование: python news_assistant.py <api_id> <api_hash>")
    sys.exit(1)

api_id = sys.argv[1]
api_hash = sys.argv[2]

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
    return news

def get_joined_news(news): # list to str
    return separator.join(news) if news else "Нет новостей."
