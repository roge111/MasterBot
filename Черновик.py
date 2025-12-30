import re
from datetime import datetime

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

print(parse_datetime("01.01.2022 00:00"))
