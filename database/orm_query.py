from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from database.models import Suggest


async def orm_add_suggest(session: AsyncSession, data: dict):
    obj = Suggest(
        user_id=data['user_id'],
        title=data['title'],
        text=data['text'],
        anon=data['anon'],
        checked=data['checked'],
        image=data['image']
    )
    
    session.add(obj)
    await session.commit()
    

async def orm_get_suggests(session: AsyncSession):
    query = select(Suggest)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_suggest(session: AsyncSession, suggest_id: int):
    query = select(Suggest).where(Suggest.id == suggest_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_suggest(session: AsyncSession, suggest_id: int, data):
    query = update(Suggest).where(Suggest.id == suggest_id).values(
        user_id=data['user_id'],
        title=data['title'],
        text=data['text'],
        anon=data['anon'],
        checked=data['checked'],
        image=data['image'])
    await session.execute(query)
    await session.commit()
    
async def orm_delete_suggest(session: AsyncSession, suggest_id: int):
    query = delete(Suggest).where(Suggest.id == suggest_id)
    await session.execute(query)
    await session.commit()