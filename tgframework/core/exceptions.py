"""
Исключения фреймворка
"""


class TgFrameworkException(Exception):
    """Базовое исключение фреймворка"""
    pass


class DatabaseException(TgFrameworkException):
    """Ошибки базы данных"""
    pass


class ConfigException(TgFrameworkException):
    """Ошибки конфигурации"""
    pass


class ValidationException(TgFrameworkException):
    """Ошибки валидации"""
    pass


class NotFoundException(TgFrameworkException):
    """Сущность не найдена"""
    pass


class APIException(TgFrameworkException):
    """Ошибки при работе с Telegram API"""
    pass

