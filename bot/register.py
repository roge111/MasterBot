from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from bot.WaitingState import WaitingState
from managers.Database import DatabaseManager
import re

db = DatabaseManager()
dp = Dispatcher()




    

class Register:
    def __init__(self):
       pass
        

    @staticmethod
    def validate_phone(phone):
        pattern = r'^\+7\d{10}$'
        return re.match(pattern, phone) is not None

        
    async def register(self, message: types.Message, state: FSMContext):
        
        await message.answer("Введите номер телефона в формате: +71234567890")
        await state.set_state(WaitingState.waiting_number)
        

    async def register_number(self, message: types.Message, state: FSMContext):
        number = message.text
        if self.validate_phone(number):
            await message.answer('Введите ФИО полностью')
            await state.update_data(number=number)
            await state.set_state(WaitingState.waiting_full_name)
        else:
            await message.answer("Неверный формат номера телефона. Пожалуйста, начните введите номер в формате: +71234567890")
            await state.clear()
            await self.register(message, state)
            
    async def register_full_name(self, message: types.Message, state: FSMContext):
        full_name = message.text
        data = await state.get_data()
        number = data.get('number')
        try:
            db.query_database(f"INSERT INTO users (tg_id, phone_number, full_name) VALUES ('{message.from_user.id}','{number}', '{full_name}')", reg=True)
            await message.answer('Вы успешно зарегистрированы')
        except Exception as e:
            await message.answer(f'Ошибка: {e}')
        
        