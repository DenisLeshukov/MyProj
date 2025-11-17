import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiosend import CryptoPay,  MAINNET
from aiosend.types import Invoice

cp = CryptoPay("488520:AAcrtc3Jsva1Zx0sMBnph1m5oIqkqtvmL7V", MAINNET)
bot = Bot("6177936866:AAF50kdxN9OPo3ZG19qsEdm1scv0dwdhR7o")
dp = Dispatcher()

@dp.message()
async def get_invoice(message: Message) -> None:
    invoice = await cp.create_invoice(10, "USDT")
    await message.answer(f"pay: {invoice.bot_invoice_url}")
    
    invoice.poll(message=message)

@cp.invoice_paid()
async def handle_payment(
    invoice: Invoice,
    message: Message,
) -> None:
    await message.answer(
        f"payment received: {invoice.amount} {invoice.asset}",
    )

async def main() -> None:
    await asyncio.gather(
        dp.start_polling(bot),
        cp.start_polling(),
    )

if __name__ == "__main__":
    asyncio.run(main())