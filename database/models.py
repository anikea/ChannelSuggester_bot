from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Text, DateTime, func


class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    

class Suggest(Base):
    __tablename__ = 'suggest_info'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(String(25))
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    text: Mapped[str] = mapped_column(Text)
    anon: Mapped[str] = mapped_column(String(5))
    image: Mapped[str] = mapped_column(String(90))
    checked: Mapped[int] = mapped_column(Integer())