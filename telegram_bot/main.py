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


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
