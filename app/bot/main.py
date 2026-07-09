import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings
from app.bot.handlers import auth, categories, transactions, budgets, balance, users
from app.bot.middlewares import CancelFSMOnMenuButtonMiddleware


async def main():
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(CancelFSMOnMenuButtonMiddleware())

    dp.include_router(auth.router)
    dp.include_router(categories.router)
    dp.include_router(transactions.router)
    dp.include_router(budgets.router)
    dp.include_router(balance.router)
    dp.include_router(users.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
