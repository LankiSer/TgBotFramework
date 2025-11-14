"""
Утилиты для работы с ботом
"""

from typing import Any, Dict, Optional


def get_user_info(user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Получить информацию о пользователе в удобном формате
    
    Args:
        user: Словарь с данными пользователя из Telegram API
        
    Returns:
        Словарь с информацией о пользователе
    """
    return {
        "id": user.get("id"),
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "full_name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        "language_code": user.get("language_code"),
        "is_bot": user.get("is_bot", False),
        "is_premium": user.get("is_premium", False),
    }


def get_chat_info(chat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Получить информацию о чате в удобном формате
    
    Args:
        chat: Словарь с данными чата из Telegram API
        
    Returns:
        Словарь с информацией о чате
    """
    return {
        "id": chat.get("id"),
        "type": chat.get("type"),
        "title": chat.get("title"),
        "username": chat.get("username"),
        "first_name": chat.get("first_name"),
        "last_name": chat.get("last_name"),
    }


def format_text(text: str, **kwargs) -> str:
    """
    Форматировать текст с подстановкой переменных
    
    Args:
        text: Текст с плейсхолдерами {variable_name}
        **kwargs: Переменные для подстановки
        
    Returns:
        Отформатированный текст
    """
    try:
        return text.format(**kwargs)
    except KeyError:
        return text


def escape_markdown(text: str) -> str:
    """
    Экранировать специальные символы для Markdown
    
    Args:
        text: Исходный текст
        
    Returns:
        Экранированный текст
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def escape_html(text: str) -> str:
    """
    Экранировать специальные символы для HTML
    
    Args:
        text: Исходный текст
        
    Returns:
        Экранированный текст
    """
    return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#039;'))


def parse_command(text: str) -> tuple[str, str]:
    """
    Парсить команду из текста
    
    Args:
        text: Текст команды (например, "/start arg1 arg2")
        
    Returns:
        Кортеж (команда, аргументы)
    """
    if not text or not text.startswith('/'):
        return "", text
    
    parts = text.split(maxsplit=1)
    command = parts[0][1:]  # Убираем /
    args = parts[1] if len(parts) > 1 else ""
    
    return command, args

