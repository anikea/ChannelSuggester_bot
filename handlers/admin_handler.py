from aiogram import Router, types, F
from keyboards.reply_keybrd import get_keyboard

from aiogram.filters import Command, or_f, StateFilter
from custom_filters.chat_type_filter import ChatTypeFilter

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import os


admin_router = Router()

admin_router.message.filter(ChatTypeFilter['private'])

ADMIN_ID = os.getenv('ADMIN_ID')

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
    