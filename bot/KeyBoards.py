
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


class Keyboard:

    
    def __init__(self):
        
        self.accept_request = '✅ Принять заявку'
        self.end = 'Завершить'
        self.cancel_request = '❌ Отменить заявку'
        self.completed_request = "🎊 Заявка выполнена"
        self.create_request = "Подать заявку"
        self.text_for_master = "🖊️ Написать мастеру"
        self.text_for_support = "⚙️ Техподдержка"
        self.feedback = "Отзыв"
        self.history_master = 'История заявок мастера'
        self.info_request = 'Информация о заявке'
        self.new_requests = 'Список новых заявок'
    def get_main_menu(self):
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=self.create_request)],
            [KeyboardButton(text=self.text_for_master)],
            [KeyboardButton(text=self.text_for_support)],
            [KeyboardButton(text=self.feedback)]
        ], resize_keyboard=True)
        return keyboard

    def get_main_menu_admin(self):
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=self.accept_request)],
            [KeyboardButton(text=self.cancel_request)],
            [KeyboardButton(text=self.completed_request)],
            [KeyboardButton(text=self.end)],
            [KeyboardButton(text=self.text_for_support)],
            [KeyboardButton(text= self.history_master)],
            [KeyboardButton(text= self.info_request)],
            [KeyboardButton(text= self.new_requests)]
        ], resize_keyboard=True)
        return keyboard
