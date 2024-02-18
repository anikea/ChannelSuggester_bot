from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import find_dotenv, load_dotenv
import asyncio
import os

from handlers.private_handler import private_router

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'), parse_mode='HTML')
dp = Dispatcher()


dp.include_router(private_router)

    
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    asyncio.run(main())