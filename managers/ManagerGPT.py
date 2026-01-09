
from dotenv import load_dotenv
from datetime import datetime


import requests
import os
import json
import re

load_dotenv()




YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')

YANDEX_GPT_URL = os.getenv('YANDEX_GPT_URL')

YANDEX_API_DIR = os.getenv('YANDEX_API_DIR')



class ManagerYandexGPT:
    def __init__(self):
        pass
    

    def parser_response_gpt(self, response) -> str:
        """Улучшенный парсер с обработкой всех крайних случаев"""
        # Удаляем лишние пробелы и переносы в начале/конце
        response = response.strip()
        
        # Проверяем баланс скобок (быстрый тест на валидность JSON)
        if response.count('{') != response.count('}'):
            raise ValueError("Несбалансированные скобки в JSON")
        
        # Экранируем только настоящие переносы, не трогая \\n
        fixed_response = re.sub(r'(?<!\\)\n', r'\\n', response)
        
        try:
            data = json.loads(fixed_response)
        except json.JSONDecodeError as e:
            # Пытаемся найти и исправить конкретную проблему
            if "Extra data" in str(e):
                # Обрезаем всё после последней закрывающей скобки
                last_brace = fixed_response.rfind('}')
                if last_brace != -1:
                    fixed_response = fixed_response[:last_brace+1]
            
            try:
                data = json.loads(fixed_response)
            except json.JSONDecodeError as final_error:
                # Выводим ошибку и проблемный участок
                error_pos = final_error.pos
                raise ValueError(
                    f"Не удалось распарсить JSON. Ошибка: {final_error}\n"
                    f"Проблемный участок: {fixed_response[max(0, error_pos-50):error_pos+50]}"
                ) from None
            
        if 'error' in data:
            return "❌Произошла ошибка с выводом ответа от ИИ. Веротяно, вы отправили пустой запрос. Если это не так, то напишите в /support и подробно опишите ситуацию."
        return data["result"]["alternatives"][0]["message"]["text"]
        

    
    def ask_yandex_gpt(self, request: str) -> str:
        try:
            system_text = 'Отвечай на вопросы по технике простыми словами. Например, "Что значит такая ошибка на такой стиральной машине и как исправить ?". Это пример. Также помогай выбирать технику для покупки. Ты помощник в боте по подаче заявок на ремонт бытовой технике и гаджетов. Если нект конкретного вопроса, уточни и напомню, чтоб заново нажали на кнопку'
            headers = {
                "Authorization": f'Api-Key {YANDEX_API_KEY}'
        }


            promt = {
            "modelUri": f"gpt://{YANDEX_API_DIR}/yandexgpt",
            "completionOptions": {
                "stream": False,
                "temperature": 0.6,
                "maxTokens": "2000",
                "reasoningOptions": {
                "mode": "DISABLED"
                }
            },
            "messages": [
                {
                "role": "system",
                "text": system_text
                },
                {
                "role": "user", 
                "text": request
                }
            ]
            }  
            response = requests.post(YANDEX_GPT_URL, headers=headers, json=promt)
            if 'error' in response and not(len(request)):
                return response, True
            result = response.text
            return result, False
            
        except Exception as e:
            return f"❌ Ошибка при исполнении: {e}.", True

