from typing import Any
from aiogram.filters import Filter
from aiogram import Bot, types


class ChatTypeFilter(Filter):
    def __init__(self, chat_type: list[str]) -> None:
        self.chat_types = chat_type
    
    async def __call__(self, message: types.Message) -> bool:
        return message.chat.type in self.chat_types