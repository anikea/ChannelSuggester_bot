from aiogram import Router, types, F, Bot
from aiogram.filters import Command, or_f
from aiogram.methods import GetChatMember
from custom_filters.chat_type_filter import ChatTypeFilter
from keyboards.reply_keybrd import get_keyboard

import os

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, or_f

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_add_suggest

from handlers.admin_handler import CHANNEL_ID

private_router = Router()
private_router.message.filter(ChatTypeFilter(['private']))


USER_KB = get_keyboard(
    "Запропонувати пост", 
    "Зв'язатися з Адміністрацією",
    placeholder="Оберіть",
    sizes=(2, )
)

bot = Bot(os.getenv("TOKEN"))

@private_router.message(StateFilter(None),Command('start'))
async def start_cmd(message: types.Message):
    chat_info = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
    if chat_info.status != 'left':
        await message.answer(
        'Вітаю! 💌 Я бот-помічник для каналу "Channel Name".\nОберіть, що хочете зробити ⬇️',
        reply_markup=USER_KB)
    else:
        await message.answer(text="<b>Схоже ви не підписані на канал!</b>\n"
                           "Підпишіться, після цього використайте команду /start "
                           "\n\n\n<a href='https://t.me/+cv1L5SHF66c1ZmQy'>КАНАЛ</a>\n\n\n", 
                     parse_mode='HTML')

    


# FMS


class SuggestPost(StatesGroup):
    
    title = State()
    text = State()
    anon = State()
    image = State()
    user_id = State()
    checked = State()
    
    texts = {
        'SuggestPost:title': 'Введіть тему(заголовок) знову',
        'SuggestPost:text': 'Введіть опис знову',
        'SuggestPost:anon': 'Введіть чи хочете запропонувати пост анонімно (Так/Ні) знову',
        'SuggestPost:image': 'Відправте фото знову',
    }


@private_router.message(StateFilter(None), F.text == "Зв'язатися з Адміністрацією")
async def connect_with_admins(message: types.Message):
    await message.answer("Функція знаходиться в розробці ❗")
    

@private_router.message(StateFilter(None), F.text == "Запропонувати пост")
async def suggest_post(message: types.Message, state: FSMContext):
    await message.answer("Введіть тему (заголовок) для посту", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SuggestPost.title)
    
    
@private_router.message(StateFilter('*'), Command('cancel'))
async def cancel_task(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Немає активних дій", reply_markup=USER_KB)
        return
    await state.clear()
    await message.answer("Дії успішно скасовано ✅", reply_markup=USER_KB)
    
    
@private_router.message(StateFilter('*'), Command('back'))
async def back_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer('Нікуди повертатись')
        return
    
    if current_state == SuggestPost.title:
        await message.answer("Введіть тему (заголовок) для посту")
    
    previous = None
    
    for step in SuggestPost.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            
            # AttributeError fix
            try:
                await message.answer(f"{SuggestPost.texts[previous.state]}")
                return
            except AttributeError:
                await state.set_state(SuggestPost.title)
        
        previous = step
    
    
@private_router.message(SuggestPost.title, F.text)
async def title_of_post(message: types.Message, state: FSMContext):
    await message.answer("Введіть текст посту")
    await state.update_data(title=message.text)
    await state.set_state(SuggestPost.text)


@private_router.message(SuggestPost.title)
async def title_of_post_dem(message: types.Message, state: FSMContext):
    await message.answer("Незрозуміле повідомлення, напишіть <b>ЗАГОЛОВОК</b> посту")


@private_router.message(SuggestPost.text, F.text)
async def text_of_post(message: types.Message, state: FSMContext):
    await message.answer("Опублікувати пост Анонімно? (Так\Ні)")
    await state.update_data(text=message.text)
    await state.set_state(SuggestPost.anon)


@private_router.message(SuggestPost.text)
async def text_of_post(message: types.Message, state: FSMContext):
    await message.answer("Незрозуміле повідомлення, напишіть <b>ТЕКСТ</b> посту")


@private_router.message(SuggestPost.anon, or_f(F.text.lower() == "так", F.text.lower() == "yes"))
async def yes_anon_post(message: types.Message, state: FSMContext):  
    await message.answer("Відправте зображення для посту")
    await state.update_data(anon=message.text)
    await state.set_state(SuggestPost.image)

    
    
@private_router.message(SuggestPost.anon, or_f(F.text.lower() == "ні", F.text.lower() == "no"))
async def no_anon_post(message: types.Message, state: FSMContext):  
    await message.answer("Відправте зображення для посту")
    await state.update_data(anon=message.text)
    await state.set_state(SuggestPost.image)


@private_router.message(SuggestPost.anon)
async def anon_of_post_dem(message: types.Message, state: FSMContext):
    await message.answer("Незрозуміле повідомлення. Напишіть лише 'Так' або 'Ні'")


@private_router.message(SuggestPost.image, F.photo)
async def img_posted(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(image=message.photo[-1].file_id)
    await state.update_data(user_id=message.from_user.id)
    await state.update_data(checked=0)
    
    data = await state.get_data()

    try:
        await orm_add_suggest(session, data)
        await message.answer("Ваш запит на пост прийнято, очікуйте підтвердження від адміністрації 😄")
        await state.clear()
    except Exception as e:
        await message.answer(
            f"Помилка: \n{str(e)}\Зверніться до сис адміна",
            reply_markup=USER_KB,
        )


@private_router.message(SuggestPost.image)
async def img_post_dem(message: types.Message, state: FSMContext):
    await message.answer("Відправте <b>ФОТО</b>")