from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from database.models import Suggest, Questions


async def orm_add_suggest(session: AsyncSession, data: dict):
    obj = Suggest(
        user_id=data['user_id'],
        title=data['title'],
        text=data['text'],
        anon=data['anon'],
        checked=int(data['checked']),
        image=data['image']
    )
    
    session.add(obj)
    await session.commit()
    

# async def orm_get_suggests(session: AsyncSession):
#     query = select(Suggest).where(Suggest.checked == 0)
#     result = await session.execute(query)
#     return result.scalars().all()

async def orm_get_pagination(session: AsyncSession, page: int):
    page_size = 5
    
    query = select(Suggest).where(Suggest.checked == 0)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_suggests(session: AsyncSession):
    query = select(Suggest).where(Suggest.checked == 0)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_suggest(session: AsyncSession, suggest_id: int):
    # Before
    # query = select(Suggest).where(Suggest.id == suggest_id)
    query = select(Suggest).where(Suggest.checked == 0) & (Suggest.id == suggest_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_suggest(session: AsyncSession, suggest_id: int, data):
    query = update(Suggest).where(Suggest.id == suggest_id).values(
        user_id=data['user_id'],
        title=data['title'],
        text=data['text'],
        anon=data['anon'],
        checked=int(data['checked']),
        image=data['image'])
    await session.execute(query)
    await session.commit()
    
    
async def orm_delete_suggest(session: AsyncSession, suggest_id: int):
    query = delete(Suggest).where(Suggest.id == suggest_id)
    await session.execute(query)
    await session.commit()
    
    
async def orm_set_checked(session: AsyncSession, suggest_id: int, data: int):
    query = update(Suggest).where(Suggest.id == suggest_id).values(
        # 0 if not and 1 if yes
        checked=data
        )
    await session.execute(query)
    await session.commit()
    
    
    # QUESTION TABLE
    
    
async def question_delete(session: AsyncSession, question_id: int):
    query = delete(Questions).where(Questions.id == question_id)
    await session.execute(query)
    await session.commit()   
    
    
async def question_pagination(session: AsyncSession, page: int):
    page_size = 1
    
    query = select(Questions).where(Questions.checked == 0)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    return result.scalars().all()


async def question_gets(session: AsyncSession):
    query = select(Questions).where(Questions.checked == 0)
    result = await session.execute(query)
    return result.scalars().all()


async def question_get_user(session: AsyncSession, question_id: int) -> int:
    result = await session.execute(select(Questions.user_id).where(Questions.id == question_id))
    user_id = result.scalar_one()
    return int(user_id)


async def question_get_text(session: AsyncSession, question_id: int) -> str:
    result = await session.execute(select(Questions.text).where(Questions.id == question_id))
    text = result.scalar_one()
    return str(text)


async def question_set_checked(session: AsyncSession, question_id: int, data: int):
    query = update(Questions).where(Questions.id == question_id).values(
        # 0 if not and 1 if yes
        checked=data
        )
    await session.execute(query)
    await session.commit()


async def question_add(session: AsyncSession, data: dict):
    obj = Questions(
        user_id=data['user_id'],
        text=data['text'],
        checked=int(data['checked']),
    )
    session.add(obj)
    await session.commit()
    

async def question_delete(session: AsyncSession, question_id: int):
    query = delete(Questions).where(Questions.id == question_id)
    await session.execute(query)
    await session.commit()