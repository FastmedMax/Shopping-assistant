import os
import re
from itertools import zip_longest, chain

import aiohttp
from loguru import logger
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.message import ContentType

from glQiwiApi import QiwiP2PClient
from glQiwiApi.qiwi.clients.p2p.types import Bill


#Данные QiWi
qiwi_p2p_client = QiwiP2PClient(secret_p2p=os.getenv("QIWI_TOKEN"))


#Данные бота
URL = os.getenv("DJANGO_HOST")
API_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Buy(StatesGroup):
    city = State()
    district = State()
    street = State()
    house = State()
    flat = State()
    category = State()
    product = State()
    amount = State()
    phone = State()
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


def validate_number(number):
    pattern = r"^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$"
    return re.match(pattern, number)


@dp.message_handler(commands="start")
async def start_cmd_handler(message: types.Message):
    """
    Разовое первое сообщение
    """
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
        "На что способен этот бот?\n"
        "«Махорка»-бот – это сервис, через который Вы можете приобрести табачные и "
        "никотиносодержащие изделия, в том числе табаки для кальяна, вейпы, pod-системы, "
        "электронные сигареты и так далее. Также у вас есть возможность купить различные "
        "приборы для курения табака, например, кальяны.\n"
        "Мы осуществляем доставку курьером до дома (или до двери) по указанному Вами адресу, чем "
        "значительно экономим Ваше время и силы на поиск нужного товара и покупку в магазине, "
        "(а демократичные цены не смогут Вас не обрадовать)."
    )

    await message.reply(text=text, reply_markup=markup)

    await cities(message)


@dp.message_handler(lambda call: call.text == "Заказать товар")
async def cities(query: types.CallbackQuery):
    """
    Выбор города
    """
    await Buy.city.set()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cities/") as response:
            if response.status == 200:
                cities = await response.json()
            else:
                logger.error(await response.text())

    markup = paginator(cities, "cities")

    text = "Пожалуйста, укажите город, в который нужно осуществить доставку"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ["previous_cities", "next_cities"], state=Buy.city)
async def turn_list_cities(call: types.CallbackQuery):
    """
    Смена листа городов
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cities/") as response:
            if response.status == 200:
                cities = await response.json()
            else:
                logger.error(await response.text())

    markup = turn_page(call, cities, "cities")

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith("cities"), state=Buy.city)
async def city(query: types.CallbackQuery, state: FSMContext):
    """
    Выбор района
    """
    await Buy.district.set()

    keyboard = list(chain(*query.message.reply_markup.inline_keyboard))
    city = next(item["text"] for item in keyboard if item["callback_data"] == query.data)
    city_id = query.data.split(":")[1]

    async with state.proxy() as data:
        data["city"] = city
        data["city_id"] = city_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cities/{city_id}/districts/") as response:
            if response.status == 200:
                districts = await response.json()
            else:
                logger.error(await response.text())

    markup = paginator(districts, "districts")

    text = "Пожалуйста, укажите район города, в который нужно осуществить доставку"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ["previous_districts", "next_districts"], state=Buy.district)
async def turn_list_districts(call: types.CallbackQuery, state: FSMContext):
    """
    Смена листа районов
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    city_id = 0

    async with state.proxy() as data:
        city_id = data["city_id"]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cities/{city_id}/districts/") as response:
            if response.status == 200:
                districts = await response.json()
            else:
                logger.error(await response.text())

    markup = turn_page(call, districts, "districts")

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith("districts"), state=Buy.district)
async def district(query: types.CallbackQuery, state: FSMContext):
    """
    Выбор улицы
    """
    await Buy.street.set()

    keyboard = list(chain(*query.message.reply_markup.inline_keyboard))
    district = next(item["text"] for item in keyboard if item["callback_data"] == query.data)
    district_id = query.data.split(":")[1]

    async with state.proxy() as data:
        data["district"] = district
        data["district_id"] = district_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/districts/{district_id}/streets/") as response:
            if response.status == 200:
                streets = await response.json()
            else:
                logger.error(await response.text())

    markup = paginator(streets, "streets")

    text = "Пожалуйста, укажите название улицы, на которую нужно осуществить доставку"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ["previous_streets", "next_streets"], state=Buy.street)
async def turn_list_streets(call: types.CallbackQuery, state: FSMContext):
    """
    Смена листа улиц
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    district_id = 0

    async with state.proxy() as data:
        district_id = data["district_id"]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/districts/{district_id}/streets/") as response:
            if response.status == 200:
                streets = await response.json()
            else:
                logger.error(await response.text())

    markup = turn_page(call, streets, "streets")

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith("streets"), state=Buy.street)
async def street(query: types.CallbackQuery, state: FSMContext):
    """
    Выбор улиц, запрос ввода дома
    """
    await Buy.house.set()

    keyboard = list(chain(*query.message.reply_markup.inline_keyboard))
    street = next(item["text"] for item in keyboard if item["callback_data"] == query.data)
    street_id = query.data.split(":")[1]

    async with state.proxy() as data:
        data["street"] = street
        data["street_id"] = street_id

    text = "Пожалуйста, укажите номер дома, к которому нужно осуществить доставку"

    await bot.send_message(chat_id=query.from_user.id, text=text)


@dp.message_handler(content_types=ContentType.TEXT, state=Buy.house)
async def house(message: types.Message, state: FSMContext):
    """
    Ввод дома, запрос ввода квартиры
    """
    await Buy.flat.set()

    async with state.proxy() as data:
        data["house"] = message.text

    text = "Введите номер квартиры"

    await bot.send_message(chat_id=message.from_user.id, text=text)


@dp.message_handler(lambda call: call.text.isnumeric(), state=Buy.flat)
async def choose_category(message: types.Message, state: FSMContext):
    """
    Заполнение адреса, выбор категории
    """
    await Buy.category.set()
    user_id = message.from_user.id
    flat = message.text

    async with state.proxy() as data:
        city = data["city"]
        district = data["district"]
        street = data["street"]
        house = data["house"]

    address = f"Город - {city}, Район - {district}, Улица - {street}, Дом - {house}, Квартира - {flat}"
    data = {"user": user_id, "address": address}

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/categories/") as response:
            if response.status == 200:
                categories = await response.json()
            else:
                logger.error(await response.text())
        async with session.post(f"{URL}/api/cart/", json=data) as response:
            if not response.status == 201:
                logger.error(await response.text())
            response = await response.json()

    async with state.proxy() as data:
        data["cart"] = response["id"]

    markup = paginator(categories, "categories")

    text = "Выберете категорию"

    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ["previous_categories", "next_categories"], state=Buy.category)
async def turn_list_categories(call: types.CallbackQuery):
    """
    Смена листа категорий
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/categories/") as response:
            if response.status == 200:
                categories = await response.json()
            else:
                logger.error(await response.text())

    markup = turn_page(call, categories, "categories")

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith("categories"), state=Buy.category)
async def choose_product(query: types.CallbackQuery, state: FSMContext):
    """
    Ввод категории, вывод товаров
    """
    await Buy.product.set()
    categories = query.data.split(":")
    id = categories[1]

    async with state.proxy() as data:
        data["category"] = id

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/categories/{id}/products/") as response:
            if response.status == 200:
                products = await response.json()
            else:
                logger.error(await response.text())

    markup = paginator(products, "products")

    text = "Пожалуйста, выберите необходимый товар из предложенного списка."

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data in ["previous_products", "next_products"], state="*")
async def turn_list_products(call: types.CallbackQuery, state: FSMContext):
    """
    Смена листа товаров
    """
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    id = 0

    async with state.proxy() as data:
        id = data["category"]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/categories/{id}/products/") as response:
            if response.status == 200:
                products = await response.json()
            else:
                logger.error(await response.text())

    markup = turn_page(call, products, "products")

    await bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith("products"), state=Buy.product)
async def process_product(query: types.CallbackQuery, state: FSMContext):
    """
    Ввод продукта, выбор колличества
    """
    await Buy.amount.set()

    product = query.data.split(":")
    id = product[1]

    async with state.proxy() as data:
        data["product"] = id
    
    markup = types.InlineKeyboardMarkup()
    
    for i in range(1, 6):
        markup.add(types.InlineKeyboardButton(text=i, callback_data=f"count:{i}"))

    text = "Пожалуйста, выберите колличество товаров"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data.startswith("count"), state=Buy.amount)
async def process_count_product(query: types.CallbackQuery, state: FSMContext):
    """
    Добавление товара к корзине, выод корзины
    """
    callback = {}

    async with state.proxy() as data:
        callback["product"] = data["product"]
        callback["cart"] = data["cart"]

    callback["count"] = query.data.split(":")[1]
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
        "Выбранные товары:\n"
    )
    for product in cart["products"]:
        text += product["product"] + " - " + str(product["count"]) + "\n"

    markup = types.InlineKeyboardMarkup(resize_keyboard=False)

    markup.row(
        types.InlineKeyboardButton("Отменить покупку", callback_data = "cancel"),
        types.InlineKeyboardButton("Добавить продукт", callback_data = "add"),
    )
    markup.add(
        types.InlineKeyboardButton("Продолжить", callback_data = "continue")
    )

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data == "cancel", state="*")
async def cancel(message: types.Message, state: FSMContext):
    """
    Отмена покупки
    """
    await state.finish()

    text = "Покупка отменена."

    await bot.send_message(chat_id=message.from_user.id, text=text)


@dp.callback_query_handler(lambda call: call.data == "add", state="*")
async def categories(query: types.CallbackQuery):
    """
    Добавление нового товара
    """
    await Buy.category.set()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/categories/") as response:
            if response.status == 200:
                categories = await response.json()
            else:
                logger.error(await response.text())

    markup = paginator(categories, "categories")

    text = "Выберете категорию"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data == "continue", state="*")
async def confirm_order(query: types.CallbackQuery, state: FSMContext):
    """
    Продолжение покупки
    """
    async with state.proxy() as data:
        cart_id = data["cart"]
        street_id = data["street_id"]

    markup = types.InlineKeyboardMarkup()

    markup.row(
        types.InlineKeyboardButton("Отменить покупку", callback_data = "cancel"),
        types.InlineKeyboardButton("Продолжить покупку", callback_data = "phone")
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cart/{cart_id}/") as response:
            if response.status == 200:
                cart = await response.json()
            else:
                logger.error(await response.text())
        async with session.get(f"{URL}/api/streets/{street_id}/") as response:
            if response.status == 200:
                street = await response.json()
            else:
                logger.error(await response.text())

    async with state.proxy() as data:
        data["total_price"] = cart["price"] + street["price"]

    text = (
        "Поздравляем! Ваш заказ был успешно сформирован\n\n"
        f"Номер Вашего заказа: {cart_id}\n"
        f"Адрес доставки: {cart['address']}\n\n"
        "Товары к оплате:\n"
    )

    for product in cart["products"]:
        text += product["product"] + " - " + str(product["count"]) + "\n"

    text += f"\nЦена за товары: {str(cart['price'])}\nЦена доставки - {str(street['price'])}"

    await bot.send_message(chat_id=query.from_user.id, text=text, reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data == "phone", state="*")
async def continue_order(query: types.CallbackQuery):
    """
    Запрос номера телефона
    """
    await Buy.phone.set()
    text = "Пожалуйста, введите номер телефона для того, чтобы мы с вами связались.\nПример:\n8-900-222-37-37"

    await bot.send_message(chat_id=query.from_user.id, text=text)


@dp.message_handler(lambda call: validate_number(call.text), state=Buy.phone)
async def phone(message: types.Message, state: FSMContext):
    """
    Оброботчик номера телефона
    """
    async with state.proxy() as data:
        cart_id = data["cart"]
        data["phone"] = message.text

    data = {"phone": message.text}

    async with aiohttp.ClientSession() as session:
        async with session.patch(f"{URL}/api/cart/{cart_id}/", json=data) as response:
            if response.status == 200:
                pass
            else:
                logger.error(await response.text())

    await payment(message, state)


@dp.message_handler(lambda call: not validate_number(call.text), state=Buy.phone)
async def incorrect_phone(message: types.Message):
    """
    Сообщение о некорректном номере телефона
    """
    text = (
        "Пожалуйста, введите ПРАВИЛЬНЫЙ номер телефона для того, чтобы мы с вами связались.\n"
        "Пример:\n"
        "8-900-222-37-37"
    )

    await bot.send_message(chat_id=message.from_user.id, text=text)


async def payment(message: types.Message, state: FSMContext):
    await Buy.payment.set()

    async with state.proxy() as data:
        total_price = data["total_price"]
        bill = await qiwi_p2p_client.create_p2p_bill(amount=total_price, pay_source_filter=["card", "qw"])
        data["bill"] = bill

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Оплатил", callback_data = "paied")
    )

    await bot.send_message(chat_id=message.from_user.id, text=f"Спасибо! Пожалуйста, оплатите товар:\n{bill.pay_url}", reply_markup=markup)


@dp.callback_query_handler(lambda call: call.data == "paied", state=Buy.payment)
async def successful_payment(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        bill = data["bill"]

    if await qiwi_p2p_client.check_if_bill_was_paid(bill):
        await bot.send_message(chat_id=query.from_user.id, text="Ваш заказ оплачен, ожидайте курьера")
        await send_order(query, state)
    else:
        await bot.send_message(chat_id=query.from_user.id, text="Заказ не оплачен, попробуйте снова")

    await state.finish()


async def send_order(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        cart_id = data["cart"]
        phone = data["phone"]

    async with aiohttp.ClientSession() as session:
        async with session.get(f"{URL}/api/cart/{cart_id}/") as response:
            if response.status == 200:
                cart = await response.json()
            else:
                logger.error(await response.text())

    text = (
        "Новый заказ:\n\n"
        f"Номер заказа: {cart_id}\n"
        f"Телефон: {phone}\n"
        f"Адрес доставки: {cart['address']}\n\n"
        "Товары к оплате:\n"
    )

    for product in cart["products"]:
        text += product["product"] + " - " + str(product["count"]) + "\n"

    admin_teltegram_token = "957140088"

    await bot.send_message(chat_id=admin_teltegram_token, text=text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
