from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram import types

class CustomStateFilter(StateFilter):
    def __init__(self, state):
        super().__init__(state)
        
    async def check(self, message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        return current_state is not None and current_state.startswith(self.state.__class__.__name__)
