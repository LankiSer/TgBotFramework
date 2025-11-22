# -*- coding: utf-8 -*-
"""
Утилиты для CLI с правильной обработкой кодировки
"""

import sys


def safe_print(message: str, prefix: str = ""):
    """
    Безопасный вывод в консоль с обработкой кодировки
    
    Args:
        message: Сообщение для вывода
        prefix: Префикс ([SUCCESS], [ERROR], и т.д.)
    """
    if prefix:
        output = f"{prefix} {message}"
    else:
        output = message
    
    try:
        print(output)
    except UnicodeEncodeError:
        # Если не удалось вывести в UTF-8, используем ASCII
        print(output.encode('ascii', errors='replace').decode('ascii'))


def success(message: str):
    """Вывод сообщения об успехе"""
    safe_print(message, "[OK]")


def error(message: str):
    """Вывод сообщения об ошибке"""
    safe_print(message, "[ERROR]")


def info(message: str):
    """Вывод информационного сообщения"""
    safe_print(message, "[INFO]")


def warning(message: str):
    """Вывод предупреждения"""
    safe_print(message, "[WARNING]")

