import json

import redis

r = redis.Redis(host="localhost", port=6379, db=0)

# Категории ---> коды
with open("include/news_categories.json", "r", encoding="utf-8") as file:
    categories = json.load(file)

# Инвертирование 0 <-> 1
invert_zero_one = {"0": "1", "1": "0"}

# Статус_строка ---> статус_булеан
status_to_bool = {"1": True, "0": False}


def get_user_channels_key(user_id: str):
    return "user:" + user_id + ":channels"


def get_user_categories_key(user_id: str):
    return "user:" + user_id + ":categories"


def get_user_readcount_key(user_id: str):
    return "user:" + user_id + ":readcount"


def do_user_registration(user_id: str):
    """Регистрирует пользователя в системе"""
    user_key = get_user_categories_key(user_id)
    user_key_readcount = get_user_readcount_key(user_id)

    with r.pipeline() as pipeline:
        pipeline.set(user_key_readcount, "5")
        for category in categories.keys():
            pipeline.hset(user_key, category, "1")
        pipeline.execute()


def sure_user_registration(user_id: str):
    """В случае необходимости, регистрирует пользователя в системе"""
    choosen_categories = get_user_categories(user_id)
    readcount = get_user_readcount(user_id)
    if set(choosen_categories.keys()) != set(categories.keys()) or readcount is None:
        do_user_registration(user_id)


def get_user_readcount(user_id: str):
    """Возвращает число считываемых для рассмотрения пользователем новостей"""
    user_key_readcount = get_user_readcount_key(user_id)

    readcount = r.get(user_key_readcount)

    if readcount is not None:
        return readcount.decode("utf-8`")
    return None


def get_user_channels(user_id: str):
    """Возвращает множество каналов, добавленных пользователем"""
    user_key = get_user_channels_key(user_id)

    channels = r.smembers(user_key)
    channels = set(map(lambda x: x.decode("utf-8`"), channels))

    return channels


def get_user_categories(user_id: str):
    """Возвращает словарь категорий, выбранных пользователем (категория ---> выбрана ли)"""
    user_key = get_user_categories_key(user_id)

    choosen_categories = r.hgetall(user_key)
    choosen_categories = {
        key.decode("utf-8`"): status_to_bool[value.decode("utf-8`")]
        for key, value in choosen_categories.items()
    }

    return choosen_categories


def change_user_readcount(user_id: str, new_readcount: str):
    user_key_readcount = get_user_readcount_key(user_id)

    with r.pipeline() as pipeline:
        pipeline.set(user_key_readcount, new_readcount)
        pipeline.execute()


def add_user_channels(user_id: str, channels_to_add):
    """Добавляет новые каналы пользователю из переданного множества"""
    user_key = get_user_channels_key(user_id)

    with r.pipeline() as pipeline:
        pipeline.sadd(user_key, *channels_to_add)
        pipeline.execute()


def remove_user_channels(user_id: str, channels_to_remove):
    """Добавляет новые каналы пользователю из переданного множества"""
    user_key = get_user_channels_key(user_id)

    with r.pipeline() as pipeline:
        pipeline.srem(user_key, *channels_to_remove)
        pipeline.execute()


def change_user_categories(user_id: str, category_to_swap):
    """Инвертирует состояние категории для пользователя"""
    user_key = get_user_categories_key(user_id)

    old_status = r.hget(user_key, category_to_swap).decode("utf-8`")
    new_status = invert_zero_one[old_status]

    with r.pipeline() as pipeline:
        pipeline.hset(user_key, category_to_swap, new_status)
        pipeline.execute()

    return "добавлена" if new_status == "1" else "удалена"
