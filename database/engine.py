import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import Base
from sqlalchemy import MetaData, Table


engine = create_async_engine(os.getenv('DB_LITE'), echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_db():
    async with engine.begin as conn:
        await conn.run_async(Base.metadata.drop_all)


async def drop_table(name: str):
    async with engine.begin() as conn:
        metadata = MetaData()
        table_to_drop = Table(name, metadata)
        await conn.run_sync(table_to_drop.drop)
