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


def turn_page(call: types.CallbackQuery, object, name):
    nav_buttons = call.message.reply_markup.inline_keyboard[-1]
    num_pages_btn = nav_buttons[1]
    current_page, count_pages = map(int, num_pages_btn.text.split("/"))

    if current_page == count_pages and call.data == f"next_{name}":
        return call.message.reply_markup
    elif current_page == 1 and call.data == f"previous_{name}":
        return call.message.reply_markup

    if call.data == f"previous_{name}":
        next_page = current_page - 1
    else:
        next_page = current_page + 1
    num_pages_btn.text = f"{next_page}/{count_pages}"
    nav_buttons[1] = num_pages_btn

    markup = types.InlineKeyboardMarkup()
    start_index_1 = current_page * 8
    if next_page == 1:
        start_index_1 = 0
    start_index_2 = start_index_1 + 1
    stop_index = next_page * 8

    for item_1, item_2 in zip_longest(object[start_index_1:stop_index:2], object[start_index_2:stop_index:2]):
        buttons = []
        if item_1:
            buttons.append(types.InlineKeyboardButton(text=item_1['title'], callback_data=f"{name}:{item_1['id']}"))
        if item_2:
            buttons.append(types.InlineKeyboardButton(text=item_2['title'], callback_data=f"{name}:{item_2['id']}"))
        markup.row(*buttons)

    markup.row(*nav_buttons)

    return markup


@dp.message_handler(commands="start")
async def start_cmd_handler(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)

    markup.add(
        types.InlineKeyboardButton("Заказать товар")
    )

    user_id = message.from_user.id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/users/{user_id}") as response:
            if response.status == 200:
                pass
            else:
                data = {"id": user_id}
                async with session.post(f"{URL}/api/users/", json=data):
                    if not response.status == 201:
                        logger.error(await response.text())

    text = (
        "Hi"
    )

    await message.reply(text=text, reply_markup=markup)


@dp.message_handler(lambda call: call.text == "Заказать товар")
async def order(query: types.CallbackQuery):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/products/") as response:
            if response.status == 200:
                products = await response.json()
            else:
                logger.error(await response.text())

    markup = paginator(products, "products")

    text = "Выберете товар"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ["previous_products", "next_products"], state="*")
async def turn_list_products(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/products/") as response:
            if response.status == 200:
                products = await response.json()
            else:
                logger.error(await response.text())

    markup = turn_page(call, products, "products")

    await bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=markup
    )


@dp.callback_query_handler(lambda call: call.data.startswith("products"))
async def product(query: types.CallbackQuery, state: FSMContext):
    await Buy.product.set()

    callback = {"user": query.from_user.id}

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/api/cart/", json=callback) as response:
            if not response.status == 201:
                logger.error(await response.text())
            response = await response.json()

    product = query.data.split(":")
    id = product[1]

    async with state.proxy() as data:
        data["product"] = id
        data["cart"] = response["id"]

    text = "Выберите колличество товара"

    await bot.send_message(chat_id=query.from_user.id, text=text)


@dp.message_handler(lambda call: call.text.isnumeric(), state=Buy.product)
async def continue_buy(message: types.Message, state: FSMContext):
    await Buy.next()

    callback = {}

    async with state.proxy() as data:
        callback["product"] = data["product"]
        callback["cart"] = data["cart"]

    callback["count"] = message.text
    cart = 0

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{URL}/api/cart/{callback['cart']}/products/", json=callback) as response:
            if not response.status == 201:
                logger.error(await response.text())
        async with session.get(f"{URL}/api/cart/{callback['cart']}/") as response:
            if response.status == 200:
                cart = await response.json()
            else:
                logger.error(await response.text())

    text = (
        "Ваши товары:\n"
    )
    for product in cart["products"]:
        text += product["product"] + " - " + str(product["count"]) + "\n"

    markup = types.InlineKeyboardMarkup(resize_keyboard=False)

    markup.row(
        types.InlineKeyboardButton("Отменить покупку", callback_data = "Cancel"),
        types.InlineKeyboardButton("Добавить продукт", callback_data = "Add"),
    )
    markup.add(
        types.InlineKeyboardButton("Продолжить", callback_data = "Continue")
    )

    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data == "Cancel", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await state.finish()

    text = "Покупака отменена"

    await bot.send_message(chat_id=message.from_user.id, text=text)


@dp.callback_query_handler(lambda call: call.data == "Add", state=Buy.amount)
async def order(query: types.CallbackQuery):
    await Buy.next()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/products/") as response:
            if response.status == 200:
                products = await response.json()
            else:
                logger.error(await response.text())

    markup = paginator(products, "products")

    text = "Выберете товар"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith("products"), state=Buy.add)
async def product(query: types.CallbackQuery, state: FSMContext):
    await Buy.product.set()

    product = query.data.split(":")
    id = product[1]

    async with state.proxy() as data:
        data["product"] = id

    text = "Выберите колличество товара"

    await bot.send_message(chat_id=query.from_user.id, text=text)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
