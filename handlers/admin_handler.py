import os

from aiogram import Router, types, F, Bot
from keyboards.reply_keybrd import get_keyboard

from aiogram.filters import Command, StateFilter
from custom_filters.chat_type_filter import ChatTypeFilter

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_set_checked, question_delete, question_get_text,question_get_user,question_set_checked
from database.orm_query import orm_delete_suggest, orm_get_suggests, orm_get_pagination, question_pagination, question_gets
from keyboards.inline import get_callback_btns




admin_router = Router()

admin_router.message.filter(ChatTypeFilter(['private', 'channel']))

ADMIN_ID = os.getenv('ADMIN_ID')

bot = Bot(os.getenv("TOKEN"))

CHANNEL_ID = -1001864149325 # Test Channel

ADMIN_KB = get_keyboard(
    "Переглянути запити [+5]",
    "Переглянути питання [+1]",
    placeholder="Оберіть",
    sizes=(2, )
)

USER_KB = get_keyboard(
    "Запропонувати пост", 
    "Зв'язатися з Адміністрацією",
    placeholder="Оберіть",
    sizes=(2, )
)


class AnswerState(StatesGroup):
    user_id = State()
    question_id = State()



@admin_router.message(StateFilter(None),F.from_user.id == int(ADMIN_ID), Command('admin'))
async def admin_command(message: types.Message):
    await message.answer(f'Вітаю пане Адміністратор', reply_markup=ADMIN_KB)


@admin_router.message(StateFilter(None),F.text == "Переглянути запити [+5]")
async def check_suggest(message: types.Message, session: AsyncSession):
    try:
        suggests = await orm_get_pagination(session, page=1)
        if suggests != []:   
            for suggest in suggests:
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
        else:
            await message.answer('Немає необроблених пропозицій')
    except Exception as e:
        await message.answer(f'Сталася помилка. Зверніться до сис. Адміна\n{str(e)}')
        
        
@admin_router.message(AnswerState.question_id, Command('cancel'))
async def cancel_task(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Немає активних дій", reply_markup=ADMIN_KB)
        return
    await state.clear()
    await message.answer("Дії успішно скасовано ✅", reply_markup=ADMIN_KB)        
        
        
@admin_router.message(Command('cancel'))
async def cancel_task(message: types.Message, state: FSMContext):
    ...
        
    
        
@admin_router.callback_query(F.data.startswith("delete_"))
async def callback_delete(callback: types.CallbackQuery, session: AsyncSession):
    suggest_id = callback.data.split('_')[-1] 
    try:
        await orm_delete_suggest(session, int(suggest_id))
        await callback.answer("Пропозиція видалена")
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        await callback.message.answer(f'Вибачте, сталася помилка, зверніться до сис. Адміністратора\n{str(e)}')
    

@admin_router.callback_query(F.data.startswith('push_deanon'))
async def callback_push(callback: types.CallbackQuery, session: AsyncSession):
    suggest_id = callback.data.split('_')[-1]
    try:
        for suggest in await orm_get_suggests(session):
            if suggest.id == int(suggest_id):
                await orm_set_checked(session=session, suggest_id=suggest_id, data=1)
                await callback.answer('Зроблено')
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=suggest.image, 
                    caption=f"{suggest.title}\
                        \n{suggest.text}\n\n<a href='tg://user?id={suggest.user_id}'><b>Автор</b></a>",
                        parse_mode='HTML',
                        )
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.answer('✅')
    except Exception as e:
        await callback.message.answer(f'Сталася помилка. Зверніться до сис. Адміна\n{str(e)}')
    

@admin_router.callback_query(F.data.startswith('push_'))
async def callback_push(callback: types.CallbackQuery, session: AsyncSession):
    suggest_id = callback.data.split('_')[-1]
    try: 
        for suggest in await orm_get_suggests(session):
            if suggest.id == int(suggest_id):
                await orm_set_checked(session=session, suggest_id=suggest_id, data=1)
                await bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=suggest.image, 
                    caption=f'{suggest.title}\
                        \n{suggest.text}\n\n<b>Анонімно</b>',
                        parse_mode='HTML',
                        )
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.answer('✅')
    except Exception as e:
        await callback.message.answer(f'Сталася помилка. Зверніться до сис. Адміна\n{str(e)}')
        
        
@admin_router.message(StateFilter(None), F.text == "Переглянути питання [+1]")
async def questions_check(message: types.Message, session: AsyncSession):
    try:
        questions = await question_pagination(session, page=1)
        if questions != []:   
            for question in questions:
                await message.answer(text=f'Питання:\n<b>{question.text}</b>',
                        parse_mode='HTML',
                        reply_markup=get_callback_btns(btns={
                            'Відповісти': f'answer_{question.id}',
                            'Видалити питання': f'remove_{question.id}'
                        })
                )
        else:
            await message.answer('Немає необроблених запитань')
    except Exception as e:
        await message.answer(f'Сталася помилка. Зверніться до сис. Адміна\n{str(e)}')
        
        
@admin_router.callback_query(F.data.startswith('answer_'))
async def callback_push(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext):
    question_id = callback.data.split('_')[-1]
    try:
        for question in await question_gets(session):
            if question.id == int(question_id):
                await state.update_data(question_id=question_id)
                await callback.message.answer(text='Введіть вашу відповідь', reply_markup=types.ReplyKeyboardRemove())
                await callback.message.edit_reply_markup(reply_markup=None)
                await callback.answer('✅')
                await state.set_state(AnswerState.question_id)
    except Exception as e:
        await callback.message.answer(f'Сталася помилка. Зверніться до сис. Адміна\n{str(e)}')
        await state.clear()
        
        
@admin_router.message(AnswerState.question_id, F.text)
async def text_answer(message: types.Message, session: AsyncSession, state: FSMContext):
    try:
        state_data = await state.get_data()
        question_id = state_data['question_id']
        user_id = await question_get_user(session, question_id)
        
        # Debug
        # print('\n\n\n\n')
        # print(user_id, question_id, text, sep='\n')
        # print('\n\n\n\n')
        
        await question_set_checked(session=session, question_id=question_id, data=1)
        
        await bot.send_message(text=f'Ви отримали відповідь на питання:\n<i>{await question_get_text(session, int(question_id))}</i>\
            \nВідповідь:\n<b>{message.text}</b>', parse_mode='HTML', chat_id=user_id)
        await message.answer('Відповідь надіслано ✅', reply_markup=ADMIN_KB)
        await state.clear()
        
    except Exception as e:
        await message.answer(f'Сталася помилка. Зверніться до сис. Адміна\n{str(e)}')
        await state.clear()
    

@admin_router.callback_query(F.data.startswith("remove_"))
async def callback_delete(callback: types.CallbackQuery, session: AsyncSession):
    question_id = callback.data.split('_')[-1] 
    try:
        await question_delete(session, int(question_id))
        await callback.answer("✅")
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        await callback.message.answer(f'Вибачте, сталася помилка, зверніться до сис. Адміністратора\n{str(e)}')