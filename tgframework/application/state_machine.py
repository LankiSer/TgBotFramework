"""
Система управления состояниями
"""

from typing import Any, Callable, Dict, Optional
from enum import Enum


class State(Enum):
    """Базовый класс для состояний"""
    NONE = "none"


class StateMachine:
    """Машина состояний для управления состояниями пользователей"""
    
    def __init__(self, db):
        """
        Инициализация машины состояний
        
        Args:
            db: Экземпляр базы данных
        """
        self.db = db
        self.handlers: Dict[str, Callable] = {}
    
    def set_state(self, user_id: int, state: str, data: Optional[Dict] = None):
        """
        Установить состояние пользователя
        
        Args:
            user_id: ID пользователя
            state: Состояние
            data: Дополнительные данные
        """
        import json
        data_str = json.dumps(data) if data else None
        self.db.set_user_state(user_id, state, data_str)
    
    def get_state(self, user_id: int) -> Optional[str]:
        """
        Получить состояние пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Состояние пользователя или None
        """
        state_data = self.db.get_user_state(user_id)
        return state_data["state"] if state_data else None
    
    def get_state_data(self, user_id: int) -> Optional[Dict]:
        """
        Получить данные состояния пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Данные состояния или None
        """
        state_data = self.db.get_user_state(user_id)
        if state_data and state_data["data"]:
            import json
            try:
                return json.loads(state_data["data"])
            except:
                return None
        return None
    
    def clear_state(self, user_id: int):
        """
        Очистить состояние пользователя
        
        Args:
            user_id: ID пользователя
        """
        self.db.clear_user_state(user_id)
    
    def register_state_handler(self, state: str, handler: Callable):
        """
        Зарегистрировать обработчик состояния
        
        Args:
            state: Состояние
            handler: Обработчик
        """
        self.handlers[state] = handler
    
    def get_state_handler(self, state: str) -> Optional[Callable]:
        """
        Получить обработчик состояния
        
        Args:
            state: Состояние
            
        Returns:
            Обработчик или None
        """
        return self.handlers.get(state)

