"""
Обработчики команд, callback и сообщений
"""

from typing import Any, Callable, Dict, Optional
import functools


class CommandHandler:
    """Обработчик команд"""
    
    def __init__(self, command: str, handler: Callable, description: Optional[str] = None):
        """
        Инициализация обработчика команды
        
        Args:
            command: Название команды (без /)
            handler: Функция-обработчик
            description: Описание команды
        """
        self.command = command.lower()
        self.handler = handler
        self.description = description
    
    async def handle(self, update: Dict[str, Any], context: Dict[str, Any]):
        """
        Обработать команду
        
        Args:
            update: Update от Telegram
            context: Контекст обработки
        """
        await self.handler(update, context)


class CallbackHandler:
    """Обработчик callback"""
    
    def __init__(self, pattern: str, handler: Callable):
        """
        Инициализация обработчика callback
        
        Args:
            pattern: Паттерн для callback_data (может начинаться с префикса)
            handler: Функция-обработчик
        """
        self.pattern = pattern
        self.handler = handler
    
    def matches(self, callback_data: str) -> bool:
        """
        Проверить, соответствует ли callback_data паттерну
        
        Args:
            callback_data: Данные callback
            
        Returns:
            True если соответствует
        """
        if callback_data.startswith(self.pattern):
            return True
        return False
    
    async def handle(self, update: Dict[str, Any], context: Dict[str, Any]):
        """
        Обработать callback
        
        Args:
            update: Update от Telegram
            context: Контекст обработки
        """
        await self.handler(update, context)


class MessageHandler:
    """Обработчик сообщений"""
    
    def __init__(self, handler: Callable, filters: Optional[Callable] = None):
        """
        Инициализация обработчика сообщений
        
        Args:
            handler: Функция-обработчик
            filters: Функция-фильтр для проверки сообщения
        """
        self.handler = handler
        self.filters = filters
    
    def should_handle(self, update: Dict[str, Any]) -> bool:
        """
        Проверить, должен ли обработчик обработать это сообщение
        
        Args:
            update: Update от Telegram
            
        Returns:
            True если должен обработать
        """
        if self.filters:
            return self.filters(update)
        return True
    
    async def handle(self, update: Dict[str, Any], context: Dict[str, Any]):
        """
        Обработать сообщение
        
        Args:
            update: Update от Telegram
            context: Контекст обработки
        """
        await self.handler(update, context)


def command(command_name: str, description: Optional[str] = None):
    """
    Декоратор для регистрации команды
    
    Args:
        command_name: Название команды
        description: Описание команды
        
    Usage:
        @command("start", "Начать работу с ботом")
        async def start_command(update, context):
            ...
    """
    def decorator(func: Callable):
        func._is_command = True
        func._command_name = command_name
        func._command_description = description
        return func
    return decorator


def callback(pattern: str):
    """
    Декоратор для регистрации callback
    
    Args:
        pattern: Паттерн для callback_data
        
    Usage:
        @callback("button_")
        async def button_handler(update, context):
            ...
    """
    def decorator(func: Callable):
        func._is_callback = True
        func._callback_pattern = pattern
        return func
    return decorator


def message_handler(filters: Optional[Callable] = None):
    """
    Декоратор для регистрации обработчика сообщений
    
    Args:
        filters: Функция-фильтр
        
    Usage:
        @message_handler(lambda u: u.get("message", {}).get("text"))
        async def text_handler(update, context):
            ...
    """
    def decorator(func: Callable):
        func._is_message_handler = True
        func._message_filters = filters
        return func
    return decorator

