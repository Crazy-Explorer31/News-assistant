import sys

from telethon import TelegramClient  # type: ignore

if len(sys.argv) != 3:
    print("Использование: python news_assistant.py <api_id> <api_hash>")
    sys.exit(1)

api_id = sys.argv[1]
api_hash = sys.argv[2]

client = TelegramClient("NewsReader", api_id, api_hash)


async def channel_exists(channel) -> bool:
    await client.start()  # Запускаем клиента
    try:
        async for message in client.iter_messages(channel, limit=1):
            return True  # Если удалось получить сообщение, канал существует
    except Exception:
        return False  # Если возникла ошибка, канал не существует
    finally:
        await client.disconnect()  # Отключаем клиента


async def get_news(channels) -> str:
    news = []
    await client.start()  # Запускаем клиента

    for channel in channels:
        try:
            async for message in client.iter_messages(
                channel, limit=4
            ):  # Получаем последнее сообщение
                news.append(f"{channel}: {message.text}")
        except Exception as e:
            news.append(f"Ошибка при получении новостей из {channel}: {str(e)}")

    await client.disconnect()  # Отключаем клиента
    return news


def highlight_heading(list_two):
    return ["⬇⬇⬇*" + list_two[0] + "*⬇⬇⬇", list_two[1].strip()]


def get_pretty_news(news):
    return [highlight_heading(item.split(":", 1)) for item in news]


def get_pretty_news_parse_mode(pretty_news):
    """Принимает список пар из `get_pretty_news` и добавляет в каждую пару parse_mode новости"""
    for i, item in enumerate(pretty_news):
        parse_mode = get_parse_mode(item[1])
        pretty_news[i].append(parse_mode)

        if item[0] == "⬇⬇⬇*" + "pitlive" + "*⬇⬇⬇":
            print(item[1])

    return pretty_news


def get_parse_mode(text: str):
    if "<" in text and ">" in text:
        parse_mode = "HTML"
    else:
        parse_mode = "Markdown"

    return parse_mode
