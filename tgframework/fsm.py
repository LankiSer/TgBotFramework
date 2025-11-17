"""
Улучшенная FSM система (как в aiogram)
"""

from typing import Any, Callable, Dict, Optional
from enum import Enum
import functools


class StatesGroup:
    """Базовый класс для групп состояний"""
    pass


class State:
    """Класс для представления состояния"""
    
    def __init__(self, state: str, group: Optional[StatesGroup] = None):
        self.state = state
        self.group = group
        self._full_state = f"{group.__name__}:{state}" if group else state
    
    def __str__(self) -> str:
        return self._full_state
    
    def __eq__(self, other) -> bool:
        if isinstance(other, State):
            return self._full_state == other._full_state
        if isinstance(other, str):
            return self._full_state == other
        return False


class FSMContext:
    """Контекст FSM для работы с состояниями"""
    
    def __init__(self, state_machine, user_id: int, chat_id: int):
        self.state_machine = state_machine
        self.user_id = user_id
        self.chat_id = chat_id
    
    async def set_state(self, state: State):
        """Установить состояние"""
        self.state_machine.set_state(self.user_id, str(state))
    
    async def get_state(self) -> Optional[str]:
        """Получить текущее состояние"""
        return self.state_machine.get_state(self.user_id)
    
    async def update_data(self, **kwargs):
        """Обновить данные состояния"""
        current_data = self.state_machine.get_state_data(self.user_id) or {}
        current_data.update(kwargs)
        self.state_machine.set_state(self.user_id, await self.get_state(), current_data)
    
    async def get_data(self) -> Dict[str, Any]:
        """Получить данные состояния"""
        return self.state_machine.get_state_data(self.user_id) or {}
    
    async def clear(self):
        """Очистить состояние и данные"""
        self.state_machine.clear_state(self.user_id)
    
    async def finish(self):
        """Завершить FSM (очистить состояние)"""
        await self.clear()


def state(state_obj: State):
    """
    Декоратор для обработчика состояния
    
    Args:
        state_obj: Состояние для обработки
        
    Example:
        @state(MyStates.waiting_for_name)
        async def handle_name(update, context):
            ...
    """
    def decorator(func: Callable):
        func._is_state_handler = True
        func._state = state_obj
        return func
    return decorator

