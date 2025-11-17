import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiosend import CryptoPay, MAINNET
from aiosend.types import Invoice
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Товары: ID → данные
CRAFTS = {
    "craft1": {
        "name": "Крафт Нож-бабочка | Легенды",
        "price": 5,
        "currency": "USDT",
        "image": "butterfly_legend.png"
    },
    "craft2": {
        "name": "Крафт Кермабит | Поверхностная закалка",
        "price": 7,
        "currency": "USDT",
        "image": "kerambit_zakal.png"
    },
    "craft3": {
        "name": "Крафт Скелетный нож | Волны",
        "price": 7,
        "currency": "USDT",
        "image": "skelet_doppler.png"
    },
    "craft4": {
        "name": "Крафт Тычковые ножи | Волны",
        "price": 3,
        "currency": "USDT",
        "image": "tichk_doppler.png"
    }
}
#50687:AAxjyaF6dQw7HioUFoxeU4RDMV6DLjxdZbR - test 488520:AAcrtc3Jsva1Zx0sMBnph1m5oIqkqtvmL7V
cp = CryptoPay("488520:AAcrtc3Jsva1Zx0sMBnph1m5oIqkqtvmL7V", MAINNET)
bot = Bot("8516331764:AAFpd68X2SSDZ9-7Bilo9s-LUZ_Qo97s0go")
dp = Dispatcher()

# Команда /start — показываем список товаров
@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🦋 Крафт Нож-бабочка | Легенды (5 USDT)", callback_data="buy_craft1")],
            [InlineKeyboardButton(text="🔪 Крафт Кермабит | Поверхностная закалка (7 USDT)", callback_data="buy_craft2")],
            [InlineKeyboardButton(text="🦴 Крафт Скелетный нож | Волны (7 USDT)", callback_data="buy_craft3")],
            [InlineKeyboardButton(text="🔪🔪 Крафт Тычковые ножи | Волны (3 USDT)", callback_data="buy_craft4")],
        ]
    )
    await message.answer(
        "Выберите крафт для покупки:",
        reply_markup=kb
    )

# Обработка нажатия на кнопку "Купить"
@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery) -> None:
    craft_id = callback.data.replace("buy_", "")
    if craft_id not in CRAFTS:
        await callback.answer("Товар не найден.")
        return

    craft = CRAFTS[craft_id]
    invoice = await cp.create_invoice(
        amount=craft["price"],
        asset=craft["currency"],
        payload=craft_id
    )

    # 🔥 ВАЖНО: связываем счёт с сообщением
    invoice.poll(message=callback.message)

    pay_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"💳 Оплатить {craft['price']} {craft['currency']}", url=invoice.bot_invoice_url)]
        ]
    )

    await callback.message.answer(
        f"Вы выбрали: {craft['name']}\nНажмите кнопку для оплаты:",
        reply_markup=pay_kb
    )
    await callback.answer()

# Обработка успешной оплаты
@cp.invoice_paid()
async def handle_payment(invoice: Invoice, message: Message) -> None:
    # ✅ Теперь message доступен!
    photo = FSInputFile(BASE_DIR / CRAFTS[invoice.payload]["image"])
    await message.answer_photo(photo=photo, caption="✅ Ваша схема:")

# Запуск
async def main() -> None:
    await asyncio.gather(
        dp.start_polling(bot),
        cp.start_polling(),
    )

if __name__ == "__main__":
    asyncio.run(main())