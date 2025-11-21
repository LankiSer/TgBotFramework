"""
Система middleware
"""

from typing import Any, Callable, Dict, List, Optional
from abc import ABC, abstractmethod


class Middleware(ABC):
    """Базовый класс для middleware"""
    
    @abstractmethod
    async def process(self, update: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Обработать update
        
        Args:
            update: Update от Telegram
            context: Контекст обработки
            
        Returns:
            True если продолжить обработку, False если остановить
        """
        pass


class MiddlewareManager:
    """Менеджер middleware"""
    
    def __init__(self):
        self.middlewares: List[Middleware] = []
    
    def add(self, middleware: Middleware):
        """
        Добавить middleware
        
        Args:
            middleware: Middleware для добавления
        """
        self.middlewares.append(middleware)
    
    async def process(self, update: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Обработать update через все middleware
        
        Args:
            update: Update от Telegram
            context: Контекст обработки
            
        Returns:
            True если продолжить обработку, False если остановить
        """
        for middleware in self.middlewares:
            result = await middleware.process(update, context)
            if not result:
                return False
        return True

