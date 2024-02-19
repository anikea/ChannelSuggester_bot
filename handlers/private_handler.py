from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from custom_filters.chat_type_filter import ChatTypeFilter
from keyboards.reply_keybrd import get_keyboard

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, or_f


private_router = Router()
private_router.message.filter(ChatTypeFilter(['private']))


USER_KB = get_keyboard(
    "Запропонувати пост", 
    "Зв'язатися з Адміністрацією",
    placeholder="Оберіть",
    sizes=(2, )
)


@private_router.message(Command('start'))
async def start_cmd(message: types.Message):
    await message.answer(
        'Вітаю! 💌 Я бот-помічник для каналу "Channel Name".\nОберіть, що хочете зробити ⬇️',
        reply_markup=USER_KB)


# FMS


class SuggestPost(StatesGroup):
    title = State()
    text = State()
    anon = State()
    image = State()

    
    #TODO зробити функціонал знизу ⬇️
    
    texts = {
        'SuggestPost:title': 'Введіть назву товару знову:',
        'SuggestPost:text': 'Введіть опис знову:',
        'SuggestPost:anon': 'Введіть вартість знову:',
        'SuggestPost:image': 'Останній стан',
    }

@private_router.message(StateFilter(None), F.text == "Зв'язатися з Адміністрацією")
async def connect_with_admins(message: types.Message):
    await message.answer("Функція знаходиться в розробці ❗")
    

@private_router.message(StateFilter(None), F.text == "Запропонувати пост")
async def suggest_post(message: types.Message, state: FSMContext):
    await message.answer("Введіть тему (заголовок) для посту ⬇️", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(SuggestPost.title)
    
    
@private_router.message(StateFilter('*'), Command('cancel'))
async def cancel_task(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Дії успішно скасовано ✅", reply_markup=USER_KB)
    
    
@private_router.message(SuggestPost.title, F.text)
async def title_of_post(message: types.Message, state: FSMContext):
    await message.answer("Введіть текст посту ⬇️")
    await state.set_state(SuggestPost.text)


@private_router.message(SuggestPost.title)
async def title_of_post_dem(message: types.Message, state: FSMContext):
    await message.answer("Незрозуміле повідомлення, напишіть ТЕКСТ посту ⬇️")


@private_router.message(SuggestPost.text, F.text)
async def text_of_post(message: types.Message, state: FSMContext):
    await message.answer("Опублікувати пост Анонімно? (Так\Ні) ⬇️")
    await state.set_state(SuggestPost.anon)


@private_router.message(SuggestPost.anon, or_f(F.text.lower() == "так", F.text.lower() == "yes"))
async def no_anon_post(message: types.Message, state: FSMContext):  
    await message.answer("(Tak) Відправте зображення для посту ⬇️")
    await state.set_state(SuggestPost.image)

    
    
@private_router.message(SuggestPost.anon, or_f(F.text.lower() == "ні", F.text.lower() == "no"))
async def yes_anon_post(message: types.Message, state: FSMContext):  
    await message.answer("(No) Відправте зображення для посту ⬇️")
    await state.set_state(SuggestPost.image)


@private_router.message(SuggestPost.anon)
async def anon_of_post_dem(message: types.Message, state: FSMContext):
    await message.answer("(НЕ ПРОЙШЛО)Незрозуміле повідомлення. Напишіть лише 'Так' або 'Ні' ⬇️")

@private_router.message(SuggestPost.image, F.photo)
async def img_post(message: types.Message, state: FSMContext):
    await message.answer("Ваш запит на пост прийнято, очікуйте підтвердження від адміністрації 😄")
    await state.clear()


@private_router.message(SuggestPost.image)
async def img_post_dem(message: types.Message, state: FSMContext):
    await message.answer("Відправте ФОТО!!!")

