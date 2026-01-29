from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from bot.WaitingState import WaitingState
from managers.Database import DatabaseManager
from datetime import datetime, timedelta
from dotenv import load_dotenv
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.KeyBoards import Keyboard
import re
import os

import urllib.parse

load_dotenv()
db = DatabaseManager()

TG_TOKEN = os.getenv('TG_TOKEN')
MASTER_ID = os.getenv('MASTER_ID')
bot = Bot(token=TG_TOKEN) 
key_board = Keyboard()


def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подать заявку", callback_data="create_request")]
    ])
    return keyboard
class Request:
    def __init__(self):
        pass

    
    @staticmethod
    def validate_address(address: str) -> bool:
        pattern = r"""
            ^                           # начало строки
            г[\.]?                    # «г.» или «г» (точка необязательна)
            \s*                     # необязательные пробелы
            (?:[а-яА-ЯёЁ0-9\-]+\s*)+  # название города (может состоять из нескольких слов)
            \s*,\s*                 # запятая с необязательными пробелами
            ул[\.]?                 # «ул.» или «ул» (точка необязательна)
            \s*                     # необязательные пробелы
            (?:[а-яА-ЯёЁ0-9\-]+\s*)+  # название улицы (может состоять из нескольких слов)
            \s*,\s*                # запятая с необязательными пробелами
            д[\.]?                  # «д.» или «д» (точка необязательна)
            \s*                    # необязательные пробелы
            \d+                   # номер дома (цифры)
            (?:\s*,\s*кв[\.]?\s*\d+)? # необязательная часть: «, кв. N» или «, кв N» (точка необязательна)
            \s*$                   # необязательные пробелы в конце + конец строки
        """
        # Удаляем комментарии и лишние пробелы из шаблона
        clean_pattern = re.sub(r'\s*#.*', '', pattern)  # убрать комментарии
        clean_pattern = re.sub(r'\n|\s{2,}', '', clean_pattern)  # убрать переносы и множественные пробелы
        
        return re.match(clean_pattern, address.strip()) is not None
    
    def get_dates_keyboard(self):
        # Создаем список кнопок
        buttons = []
        today = datetime.now()
        
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime("%d.%m.%Y")
            callback_data = f"date_{date.strftime('%Y-%m-%d')}"
            buttons.append([InlineKeyboardButton(text=date_str, callback_data=callback_data)])
        
        # Передаем кнопки в конструктор
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard


# Генерация клавиатуры со временем
    def get_times_keyboard(self):
        times = ["09:00", "10:00", "11:00", "12:00",
                "13:00", "14:00", "15:00", "16:00",
                "17:00", "18:00", "19:00", "20:00"]
        
        buttons = []
        for i in range(0, len(times), 4):
            row = []
            for j in range(i, min(i + 4, len(times))):
                row.append(InlineKeyboardButton(text=times[j], callback_data=f"time_{times[j]}"))
            buttons.append(row)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard

    @staticmethod
    def validate_datetime(value: str) -> bool:
        """
        Проверяет, соответствует ли строка формату ДД.ММ.ГГГГ ЧЧ:ММ и является ли дата/время валидными.
        
        Args:
            value (str): Строка для проверки.
        
        Returns:
            bool: True, если формат и значение корректны, иначе False.
        """
        # Шаг 1. Проверка формата через регулярное выражение
        pattern = r'^(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2})$'
        match = re.match(pattern, value)
        if not match:
            return False

        day, month, year, hour, minute = map(int, match.groups())

        # Шаг 2. Проверка диапазона значений
        if not (1 <= month <= 12):
            return False
        if not (0 <= hour <= 23):
            return False
        if not (0 <= minute <= 59):
            return False

        # Шаг 3. Проверка существования даты (с учётом високосных годов)
        try:
            datetime(year, month, day, hour, minute)
            return True
        except ValueError:
            return False
    @staticmethod
    def parse_datetime(input_str: str) -> str | None:
        """
        Преобразует строку из формата ДД.ММ.ГГГГ ЧЧ:ММ в YYYY-MM-DD HH:MI:SS.
        Секунды устанавливаются как 00.
        
        Args:
            input_str (str): Строка в формате ДД.ММ.ГГГГ ЧЧ:ММ
            
        Returns:
            str: Строка в формате YYYY-MM-DD HH:MI:SS или None, если формат невалиден.
        """
        # Регулярное выражение для проверки формата
        pattern = r'^(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2})$'
        match = re.match(pattern, input_str)
        
        if not match:
            return None  # Неверный формат
        
        day, month, year, hour, minute = map(int, match.groups())
        
        # Проверка допустимых диапазонов
        if not (1 <= day <= 31):
            return None
        if not (1 <= month <= 12):
            return None
        if not (0 <= hour <= 23):
            return None
        if not (0 <= minute <= 59):
            return None
            
        # Проверка корректности дня в месяце
        try:
            datetime(year, month, day, hour, minute)
        except ValueError:
            return None
        
        # Форматирование в строку YYYY-MM-DD HH:MI:SS
        return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"

    @staticmethod
    def validate_request_id(request_id):
        try:
            res = db.query_database(f'select 1 from requests where request_id = {request_id}')
            return len(res) and res[0][0]
        except Exception as e:
            return None

    @staticmethod
    def check_completed(request_id):
        status = db.query_database(f"select 1 from requests where request_id = {request_id} and status = 'completed'" )
        return len(status) and status[0][0]
    async def request_start(self, message: types.Message, state: FSMContext):
        await message.answer("Введите свой адрес для заявки в формате: г. Мурманск, ул. Папанина, д. 11, кв. 3 (пример)")
        await state.set_state(WaitingState.waiting_address)
    

    async def request_address(self, message: types.Message, state: FSMContext):
        address = message.text
        if self.validate_address(address):
            await message.answer('Опишите название технике как можно подробнее (желательно указать модель). Например: стиральная машина LG DirectDrive 8')
            await state.update_data(address = address)
            await state.set_state(WaitingState.waiting_technical_info)
        else:
            await message.answer('Не верный формат.')
            await self.request_start(message, state)
           
    
    async def request_tech_info(self, message: types.Message, state: FSMContext):
        info = message.text


        await message.answer('Опишите проблему с техникой. Например: не работает кнопка включения')
        await state.update_data(info = info)
        await state.set_state(WaitingState.waiting_description)

    async def request_description(self, message: types.Message, state: FSMContext):
        description = message.text

        
        
        

        data = await state.get_data()
        address = data.get('address')
        info = data.get('info')

        # Получаем текущее время
        now = datetime.now()

        # Форматируем в нужный вид
        date_now = now.strftime("%Y-%m-%d %H:%M:%S")

        
        try:
            data_of_user = db.query_database(f"SELECT user_id, phone_number FROM users WHERE tg_id = {message.from_user.id}")

            if len(data_of_user) == 0:
                await message.answer('Произошла ошибка. Сообщите проблему в техподдержку', reply_markup=key_board.get_main_menu_admin())

                return
            

            user_id = data_of_user[0][0]
            phone_number = data_of_user[0][1]


            db.query_database(f"INSERT INTO requests (user_id, address, technical_type, description, date_create, phone_number, status) VALUES ({user_id}, '{address}', '{info}', '{description}', '{date_now}', '{phone_number}', 'new')", reg=True)
            await message.answer('Заявка отправлена. Ожидайте, Вам напишет или позвонит мастер.')
            result = db.query_database('SELECT request_id FROM requests ORDER BY request_id DESC LIMIT 1;')
            if not(len(result)):
                await message.answer('Возникла ошибка, обратитесь в поддержку')
                return 
            message_master = f'Пришла новая заявка с id={result[0][0]} от пользователя с телеграмм_id = {message.from_user.id}:\n Телефон - {phone_number},\n Адрес - {address}, Точка на карте: https://yandex.ru/maps/?text={urllib.parse.quote(address)}, Техника - {info}\n Описание проблемы: \n {description}.'
            await bot.send_message(chat_id=MASTER_ID, text=message_master)
        except Exception as e:
            message.answer(f"Ошибка: {e}")
        await state.clear()


    async def request_accept(self, message: types.Message, state: FSMContext, user_id: int):
        
        
        if user_id == int(MASTER_ID):
            await message.answer('Введите id заявки')
            await state.update_data(type_command = 'accept')
            await state.set_state(WaitingState.waiting_id_request)
    
    async def accept_wait_id(self, message: types.Message, state: FSMContext):
        request_id = message.text
        data = await state.get_data()
        type_command = data.get('type_command')
        if self.validate_request_id(request_id):
            if type_command == 'accept':
                
                await message.answer(f'Введите дату начала периода: ', reply_markup=self.get_dates_keyboard())
                await state.update_data(request_id = request_id)
                await state.set_state(WaitingState.waiting_date)
                
            elif type_command == 'cancel':
                # Проверяем, что пользователь является мастером, назначенным на заявку
                
                
                db.query_database(f"UPDATE requests SET status = 'canceled' WHERE request_id = {request_id}", reg=True)
                await message.answer('Заявка отменена')
                tg_id = db.query_database(f"SELECT users.tg_id FROM requests JOIN users ON requests.user_id = users.user_id WHERE requests.request_id = {request_id}")[0][0]
                await bot.send_message(chat_id=tg_id, text=f'Ваша заявка с id={request_id} отменена.')
                await state.clear()
                await message.answer("Главное меню:", reply_markup=key_board.get_main_menu_admin())
                
            elif type_command == 'completed':
                # Проверяем, что пользователь является мастером, назначенным на заявку
                master_check = db.query_database(f"SELECT masters.tg_id FROM requests JOIN masters ON requests.master_id = masters.id WHERE request_id = {request_id}")
                if master_check and master_check[0][0] == message.from_user.id:
                    db.query_database(f"UPDATE requests SET status = 'completed' WHERE request_id = {request_id}", reg=True)
                    await message.answer('Заявка выполнена')
                    tg_id = db.query_database(f"SELECT users.tg_id FROM requests JOIN users ON requests.user_id = users.user_id WHERE requests.request_id = {request_id}")[0][0]
                    await bot.send_message(chat_id=tg_id, text=f'Ваша заявка с id={request_id} выполнена.')
                    await message.answer("Главное меню:", reply_markup=key_board.get_main_menu_admin())
                else:
                    await message.answer('Вы не можете отметить эту заявку как выполненную, так как вы не являетесь назначенным мастером.')
                    await state.clear()
            elif type_command == 'feedback':
                # Проверяем, что заявка выполнена
                if not self.check_completed(request_id):
                    await message.answer('Отзыв можно оставить только для выполненной заявки')
                    await self.feedback(message, state)
                    return
                
                # Проверяем, что отзыв еще не оставляли
                feedback_check = db.query_database(f"SELECT 1 FROM feedbacks WHERE request_id = {request_id}")
                if feedback_check:
                    await message.answer('Отзыв уже оставлен для этой заявки')
                    await state.clear()
                    return
                    
                await message.answer('Введите отзыв')
                await state.update_data(request_id = request_id)
                await state.set_state(WaitingState.waiting_feedback)
            elif type_command == 'info_request':
                role = data.get('role')
                if role == 'user':
                    user_id = db.query_database(f'select user_id from users where tg_id = {message.from_user.id}')
                    if not(user_id):
                        await message.answer('Произошла ошибка, вы не зарегестрированы. Напишите в поддержку или введите /start')
                        return
                    request = db.query_database(f'select * from requests where request_id = {request_id} and user_id = {user_id[0][0]}')
                    if not(request):
                        await message.answer('Неверно указан номер заявки или же это не ваша заявка.')
                        await self.info_request(message, state)
                        return
                else:
                    master_id = db.query_database(f'select id from masters where tg_id = {message.from_user.id}')[0][0]
                    request = db.query_database(f'select * from requests where request_id = {request_id} and master_id = {master_id}')
                    if not(request):
                        await message.answer('Неверно указан номер заявки или же это не ваша заявка.')
                        await self.info_request(message, state)
                        return 
                    
                request = request[0]
                print(request)
                answer_message = f"Информация по заявка с номером (id) = {request[0]}"
                answer_message += f"\n Номер телефона клиента: {request[2]}"
                answer_message += f"\n Адрес клиента: {request[3]}"
                answer_message += f"\n Тип техники: {request[4]}"
                answer_message += f"\n Описание поломки: {request[5]}"
                answer_message += f"\n Дата и время создания в формате ГГГГ-ММ-ДД: {request[6]}"
                if request[7]:  # date_work_start
                    answer_message += f"\n Дата начала периода: {request[7]}"
                if request[9]:  # date_work_end
                    answer_message += f"\n Дата окончания периода: {request[10]}"
                if request[8] == 'in_work':
                    answer_message += f"\n Статус: в работе"
                elif request[8] == 'completed':
                    answer_message += "\n Статус: выполнена"
                elif request[8] == 'canceld':
                    answer_message += "\n Статус: отменена"
                elif request[8] == 'new':
                    answer_message += "\n Статус: новая"
                await message.answer(answer_message)



        else:
                await message.answer('Неверный id. Начните заново.', reply_markup=key_board.get_main_menu_admin())
                
                await state.clear()


    async def accept_wait_date_start(self, callback_query: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        request_id = data.get('request_id')
        date = callback_query.data.replace('date_', '')
        await state.update_data(date=date)
       
        master_id = db.query_database(f'select id from masters where tg_id = {callback_query.from_user.id}')
        if not(master_id):
            await callback_query.message.answer('Ошибка чтения мастера. Возможно вы им не являетесь.')
            return
        

        await callback_query.message.edit_text(
            f"Дата: {date}\n⏰ Теперь выберите время:",
            reply_markup=self.get_times_keyboard()
        )
        await callback_query.answer()
        await state.set_state(WaitingState.waiting_time_start)
    async def process_time_fsm(callback_query: types.CallbackQuery, state: FSMContext):
        async with state.proxy() as data:
            data['time'] = callback_query.data.replace('time_', '')
            await callback_query.message.answer(
                f"Теперь введите дату окончания периода"
            )
        
        await state.set_state(WaitingState.waiting_date_end)
        await callback_query.answer()

    # Функция для обработки ввода даты окончания периода
    async def accept_end_date(message: types.Message, state: FSMContext, self):
        await message.answer(f'Введите дату окончания периода: ', reply_markup=self.get_dates_keyboard())
        await state.set_state(WaitingState.waiting_date)
    async def accept(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        request_id = data.get('request_id')
        date = message.text

        if not(self.validate_datetime(date)):
            await message.answer('❌Неверный формат даты')
            await self.accept_wait_date_start(message, state)
        
        date_format = self.parse_datetime(date)

        master_id = db.query_database(f'select id from masters where tg_id = {message.from_user.id}')
        if not(master_id):
            await message.answer('Ошибка чтения мастера. Возможно вы им не являетесь.')
            return
        

        db.query_database(f"UPDATE requests SET date_work_end = '{date_format}' WHERE request_id = {request_id}", reg=True)
        await message.answer('Дата окончания периода принята')
        tg_id = db.query_database(f"SELECT users.tg_id FROM requests JOIN users ON requests.user_id = users.user_id WHERE requests.request_id = {request_id}")[0][0]
        await bot.send_message(chat_id=tg_id, text=f'В заявке с id={request_id} установлена дата окончания периода: {date}.')

    async def cancel_request(self, message: types.Message, state: FSMContext):
        await message.answer('Введите id заявки')
        await state.update_data(type_command = 'cancel')
        await state.set_state(WaitingState.waiting_id_request)
    
    async def copleted_request(self, message: types.Message, state: FSMContext):
        await message.answer('Введите id заявки')
        await state.update_data(type_command = 'completed')
        await state.set_state(WaitingState.waiting_id_request)

    async def feedback(self, message: types.Message, state: FSMContext):
        await message.answer('Введите id заявки. Но обратите внимание, что заявка должна быть выполнена')
        await state.update_data(type_command = 'feedback')
        await state.set_state(WaitingState.waiting_id_request)
    async def feedback_wait_text(self, message: types.Message, state: FSMContext):
        await message.answer('Введите оценку от 1 до 5')
        await state.update_data(text_feedback = message.text)
        await state.set_state(WaitingState.waiting_mark)

    async def feedback_mark(self, message: types.Message, state: FSMContext):
        mark = message.text

        if mark.isdigit() and int(mark) in range(1, 6):
            data = await state.get_data()
            request_id = data.get('request_id')
            text_feedback = data.get('text_feedback')
            
            # Получаем master_id из таблицы requests
            master_result = db.query_database(f"SELECT master_id FROM requests WHERE request_id = {request_id}")
            
            if not master_result:
                await message.answer('Заявка не найдена')
                await state.clear()
                return
                
            master_id = master_result[0][0]
            print(master_id)
            
            # Проверяем, что заявка выполнена
            status_result = db.query_database(f"SELECT status FROM requests WHERE request_id = {request_id}")
            if not status_result or status_result[0][0] != 'completed':
                await message.answer('Отзыв можно оставить только для выполненной заявки')
                await state.clear()
                return
            
            # Вставляем отзыв в таблицу feedbacks
            db.query_database(f"INSERT INTO feedbacks (feedback, mark, request_id) VALUES ('{text_feedback}', {mark}, {request_id})", reg=True)
            
            # Получаем текущую среднюю оценку мастера
            avg_result = db.query_database(f"SELECT average_mark FROM masters WHERE id = {master_id}")
            if not avg_result:
                await message.answer('Мастер не найден')
                await state.clear()
                return
                
            current_avg = float(avg_result[0][0]) if avg_result[0][0] else 0.0
            
            # Получаем количество отзывов мастера
            count_result = db.query_database(f"SELECT COUNT(*) FROM feedbacks f JOIN requests r ON f.request_id = r.request_id WHERE r.master_id = {master_id}")
            feedback_count = int(count_result[0][0]) if count_result and count_result[0][0] else 0
            
            # Вычисляем новую среднюю оценку
            new_avg = round((current_avg * (feedback_count - 1) + int(mark)) / feedback_count, 2) if feedback_count > 0 else float(mark)
            
            # Обновляем среднюю оценку мастера
            db.query_database(f"UPDATE masters SET average_mark = {new_avg} WHERE id = {master_id}", reg=True)
            
            await message.answer(f'Спасибо за ваш отзыв! Новая средняя оценка мастера: {new_avg}', reply_markup=key_board.get_main_menu())
            master_tg_id = db.query_database(f"SELECT tg_id FROM masters WHERE id = {master_id}")[0][0]
            await bot.send_message(master_tg_id, f'Вам оставили отзыв:\n Заявка {request_id}\nОценка: {mark}\nТекст отзыва: {text_feedback}\n   Новая средняя оценка Ваша: {new_avg}')
            await state.clear()
        else:
            await message.answer('Неверный формат оценки')
            await self.feedback_wait_text(message, state)
        


    async def history_master(self, message: types.Message, state: FSMContext):

        master_id = db.query_database(f'select id from masters where tg_id = {message.from_user.id}')

        if not(master_id):
            await message.answer('Вы не являетесь мастером или произошла ошибка')
            return 

        requests = db.query_database(f"SELECT request_id, phone_number, status FROM requests WHERE master_id = {master_id[0][0]} AND ((status IN ('new', 'in_work')) OR (status = 'completed' AND date_work_end >= CURRENT_DATE - INTERVAL '1 month'));")

        answer_message = 'История заявок:\n'
        for request in requests:
            if request[2] == 'completed':
                status = 'выполнена'
            elif request[2] == 'in_work':
                status = 'в работе'
            else:
                status = 'новая'
            answer_message += f'ID заявка: {request[0]} - номер телефона: {request[1]} - статус: {status}\n'
        
        await message.answer(answer_message)
    async def info_request(self, message: types.Message, state: FSMContext):
        master_check = db.query_database(f'select id from masters where tg_id = {message.from_user.id}')
        if not(master_check):
            await state.update_data(role = 'user')
        else:
            await state.update_data(role = 'master')
        

        await message.answer('Укажите id заявки, информацию по которой хотите получить.')
        await state.update_data(type_command = 'info_request')
        await state.set_state(WaitingState.waiting_id_request)
    

    async def new_requests(self, message: types.Message):
        master_check = db.query_database(f"select id from masters where tg_id = {message.from_user.id}")
        if not(master_check):
            await message.answer('Вы не являетесь мастером или обратитесь в поддержку')
            return
        
        requests = db.query_database(f"SELECT request_id, phone_number FROM requests WHERE status = 'new';")
        answer_message = 'Необработанные заявки:\n'
        for request in requests:
            
            answer_message += f'ID заявка: {request[0]} - номер телефона: {request[1]}\n'
        await message.answer(f'{answer_message}\nЧтобы посмотреть подробнее информацию про заявку, воспользуйтесь отдельной кнопкой "Информация о заявке".', reply_markup=key_board.get_main_menu_admin())
