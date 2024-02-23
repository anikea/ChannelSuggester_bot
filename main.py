from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import os

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from handlers.private_handler import private_router
from handlers.admin_handler import admin_router

from database.engine import create_db, drop_db, session_maker
from database.db import DBSession

bot = Bot(token=os.getenv('TOKEN'), parse_mode='HTML')
dp = Dispatcher()


dp.include_router(admin_router)
dp.include_router(private_router)
    
async def on_startup(bot):
    await create_db()


async def on_shutdown(bot):
    print('bot lig')
    
    
async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    dp.update.middleware(DBSession(session_pool=session_maker))
    
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=types.BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())