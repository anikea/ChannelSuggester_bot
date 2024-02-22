from aiogram import Router, types, F, Bot
from keyboards.reply_keybrd import get_keyboard

from aiogram.filters import Command, or_f, StateFilter
from custom_filters.chat_type_filter import ChatTypeFilter

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_suggest, orm_delete_suggest, orm_get_suggest, orm_update_suggest, orm_get_suggests
from keyboards.inline import get_callback_btns
from aiogram.utils.markdown import link


import os


admin_router = Router()

admin_router.message.filter(ChatTypeFilter(['private', 'channel']))

ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(os.getenv("TOKEN"))

CHANNEL_ID = -1001864149325 # Test Channel

ADMIN_KB = get_keyboard(
    "Переглянути запити",
    "Переглянути повідомлення",
    placeholder="Оберіть",
    sizes=(2, )
)

USER_KB = get_keyboard(
    "Запропонувати пост", 
    "Зв'язатися з Адміністрацією",
    placeholder="Оберіть",
    sizes=(2, )
)


@admin_router.message(F.from_user.id == int(ADMIN_ID), Command('admin'))
async def admin_command(message: types.Message):
    await message.answer(f'Вітаю пане Адміністратор', reply_markup=ADMIN_KB)


@admin_router.message(F.text == "Переглянути запити")
async def check_suggest(message: types.Message, session: AsyncSession):
    for suggest in await orm_get_suggests(session):
        await message.answer_photo(
            suggest.image,
            caption=f'<strong>{suggest.title}\
                </strong>\n{suggest.text}\nАнонімно: {suggest.anon}',
                parse_mode='HTML',
                reply_markup=get_callback_btns(btns={
                    'Опублікувати анонімно': f'push_{suggest.id}',
                    'Опублікувати відкрито': f'push_deanon_{suggest.id}',
                    'Видалити пропозицію': f'delete_{suggest.id}'
                })
        )

@admin_router.callback_query(F.data.startswith("delete_"))
async def callback_delete(callback: types.CallbackQuery, session: AsyncSession):

    suggest_id = callback.data.split('_')[-1] 
    
    await orm_delete_suggest(session, int(suggest_id))
    
    await callback.answer("Пропозиція видалена")
    

@admin_router.callback_query(F.data.startswith('push_deanon'))
async def callback_push(callback: types.CallbackQuery, session: AsyncSession):
    suggest_id = callback.data.split('_')[-1]
    for suggest in await orm_get_suggests(session):
        if suggest.id == int(suggest_id):
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=suggest.image, 
                caption=f'{suggest.title}\
                    \n{suggest.text}\n[User](tg://user?id={suggest.user_id})',
                    parse_mode='MarkdownV2',
                    )
    

@admin_router.callback_query(F.data.startswith('push_'))
async def callback_push(callback: types.CallbackQuery, session: AsyncSession):
   await callback.message.answer('Опубліковано анонімно')
    

