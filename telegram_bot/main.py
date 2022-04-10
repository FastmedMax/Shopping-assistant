import os
from itertools import zip_longest, chain

import aiohttp
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType


URL = os.getenv("DJANGO_HOST")
API_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Buy(StatesGroup):
    product = State()
    amount = State()
    add = State()
    city = State()
    district = State()
    street = State()
    house = State()
    payment = State()


def paginator(objects, name) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()

    num_pages = len(objects) // 8
    if len(objects) % 8:
        num_pages += 1
    if num_pages == 0:
        num_pages = 1

    for item_1, item_2 in zip_longest(objects[0:8:2], objects[1:8:2]):
        buttons = []
        if item_1:
            buttons.append(types.InlineKeyboardButton(text=item_1['title'], callback_data=f"{name}:{item_1['id']}"))
        if item_2:
            buttons.append(types.InlineKeyboardButton(text=item_2['title'], callback_data=f"{name}:{item_2['id']}"))
        markup.row(*buttons)

    markup.row(
        types.InlineKeyboardButton("Назад", callback_data=f"previous_{name}"),
        types.InlineKeyboardButton(f"1/{num_pages}", callback_data="page_count"),
        types.InlineKeyboardButton("Далее", callback_data=f"next_{name}"),
    )

    return markup

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
