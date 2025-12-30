from pathlib import Path
import sys
import os

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from managers.Database import DatabaseManager
from bot.register import Register
from bot.Request import Request
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from bot.WaitingState import WaitingState
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.KeyBoards import Keyboard
import asyncio
import logging
from aiogram.fsm.context import FSMContext

# Загрузка переменных окружения
load_dotenv()

db = DatabaseManager()
TG_BOT_TOKEN = os.getenv('TG_TOKEN')
bot = Bot(token=TG_BOT_TOKEN)
register = Register()
request = Request()
dp = Dispatcher()
key_board = Keyboard()

MASTER_ID = os.getenv('MASTER_ID')
SUPPORT_ID = os.getenv('SUPPORT_ID')


# Проверка, зарегистрирован ли пользователь

def is_user(tg_id):
    res = db.query_database(f'select 1 from users where tg_id = {tg_id}')

    return len(res) and str(res[0][0]) == '1'
# Главное меню с inline-кнопками


# Обработчик /start — показываем главное меню
@dp.message(Command('start'))
async def register_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Приветствую в боте! Я доктор техники и помогу разобраться с проблемой.\n\n'
        'У меня вы можете:\n'
        '- создать заявку на вызов мастера\n'
        '- обратиться за советом к нейросети\n\n'
        'При возникновении ошибок или для помощи используйте кнопку "Поддержка"\n\n'
       
    )

    if is_user(message.from_user.id):
        
        if message.from_user.id == int(MASTER_ID):
            await message.answer("Главное меню:", reply_markup=key_board.get_main_menu_admin())
        else:
            await message.answer("Главное меню:", reply_markup=key_board.get_main_menu())
    else:
        await message.answer("Давайте зарегестрируемся")
        await register.register(message, state)



# Обработчик нажатия кнопки "Регистрация"
@dp.callback_query(F.data == "register")
async def handle_register(callback: types.CallbackQuery, state: FSMContext):
    await register.register(callback.message, state)
    await callback.answer()

# Обработчик нажатия кнопки "Подать заявку"
@dp.message(F.text == key_board.create_request)
async def handle_create_request(message: types.Message, state: FSMContext):
    await request.request_start(message, state)
    

# Существующие обработчики (без изменений)
@dp.message(Command('register'))
async def register_reg(message: types.Message, state: FSMContext):
    await register.register(message, state)

@dp.message(WaitingState.waiting_number)
async def register_number_handler(message: types.Message, state: FSMContext):
    await register.register_number(message, state)

@dp.message(WaitingState.waiting_full_name)
async def register_full_name_handler(message: types.Message, state: FSMContext):
    await register.register_full_name(message, state)
    if message.from_user.id == int(MASTER_ID):
        await message.answer("Главное меню:", reply_markup=key_board.get_main_menu_admin())
    else:
        await message.answer("Главное меню:", reply_markup=key_board.get_main_menu())
    await state.clear()
   

@dp.message(Command('create_request'))
async def create_request(message: types.Message, state: FSMContext):
    await request.request_start(message, state)

@dp.message(WaitingState.waiting_address)
async def wait_address_request(message: types.Message, state: FSMContext):
    await request.request_address(message, state)

@dp.message(WaitingState.waiting_technical_info)
async def wait_technical_info_request(message: types.Message, state: FSMContext):
    await request.request_tech_info(message, state)

@dp.message(WaitingState.waiting_description)
async def wait_description_request(message: types.Message, state: FSMContext):
    await request.request_description(message, state)

    print(message.from_user.id)
    if message.from_user.id == int(MASTER_ID):
        await message.answer("Главное меню:", reply_markup=key_board.get_main_menu_admin())
    else:
        await message.answer("Главное меню:", reply_markup=key_board.get_main_menu())
    await state.clear()


@dp.message(F.text == f"{key_board.accept_request}")
async def accept_request(message: types.Message, state: FSMContext):
    
    await request.request_accept(message, state, message.from_user.id)

@dp.message(WaitingState.waiting_id_request)
async def accept_request_id(message: types.Message, state: FSMContext):
    await request.accept_wait_id(message, state)
@dp.message(WaitingState.waiting_date)
async def accept_request_date(message: types.Message, state: FSMContext):
    await request.accept_wait_date_start(message, state)

@dp.message(WaitingState.waiting_date_end)
async def accept_request_date_end(message: types.Message, state: FSMContext):
    await request.accept(message, state)
    if message.from_user.id == int(MASTER_ID):
        await message.answer("Главное меню:", reply_markup=key_board.get_main_menu_admin())
    else:
        await message.answer("Главное меню:", reply_markup=key_board.get_main_menu())
    await state.clear()


@dp.message(F.text == key_board.new_requests)
async def list_new_requests(message: types.Message):
    await request.new_requests(message)


@dp.message(F.text == key_board.cancel_request)
async def cancel_request(message: types.Message, state: FSMContext):
    await request.cancel_request(message, state)

@dp.message(F.text == key_board.completed_request)
async def completed_request(message: types.Message, state: FSMContext):
    await request.copleted_request(message, state)



@dp.message(F.text == key_board.text_for_master)
async def message_to_master(message: types.Message, state: FSMContext):
    await message.answer('Введите сообщение для мастера')
    await state.set_state(WaitingState.waiting_message_to_master)


@dp.message(WaitingState.waiting_message_to_master)
async def message_to_master_handler(message: types.Message, state: FSMContext):
    await bot.send_message(MASTER_ID, message.text)
    await message.answer('✅Сообщение отправлено')
    await state.clear()


@dp.message(F.text == key_board.text_for_support)
async def message_to_support(message: types.Message, state: FSMContext):
    await message.answer('Введите сообщение для поддержки')
    await state.set_state(WaitingState.waiting_message_to_support)

@dp.message(WaitingState.waiting_message_to_support)
async def message_to_support_handler(message: types.Message, state: FSMContext):
    await bot.send_message(SUPPORT_ID, message.text)
    await message.answer('Сообщение отправлено')
    await state.clear()




@dp.message(F.text == key_board.feedback)
async def feedback(message: types.Message, state: FSMContext):
    await request.feedback(message, state)

@dp.message(WaitingState.waiting_id_request)
async def feedback_id_request(message: types.Message, state: FSMContext):
    await request.accept_wait_id(message, state)

@dp.message(WaitingState.waiting_feedback)
async def feedback_text(message: types.Message, state: FSMContext):
    await request.feedback_wait_text(message, state)
@dp.message(WaitingState.waiting_mark)
async def feedback_mark(message: types.Message, state: FSMContext):
    await request.feedback_mark(message, state)




@dp.message(F.text == key_board.history_master)
async def history_requests_masters(message: types.Message, state: FSMContext):
    await request.history_master(message, state)


@dp.message(F.text == key_board.info_request)
async def info_request(message: types.Message, state: FSMContext):
    await request.info_request(message, state)

# Дополнительные обработчики для возврата в меню после завершения процессов


@dp.message(F.text == key_board.end)
async def finish_process(message: types.Message, state: FSMContext):
    """Кнопка для возврата в главное меню из любого состояния"""
    await state.clear()
    await message.answer("Главное меню:", reply_markup=key_board.get_main_menu_admin())

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
