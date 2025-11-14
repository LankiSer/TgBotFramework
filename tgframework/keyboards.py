"""
Построители клавиатур для Telegram
"""

from typing import List, Dict, Any, Optional


class InlineKeyboardBuilder:
    """Построитель inline клавиатур"""
    
    def __init__(self):
        self.buttons: List[List[Dict[str, Any]]] = []
        self.current_row: List[Dict[str, Any]] = []
    
    def add_button(self, text: str, callback_data: Optional[str] = None,
                   url: Optional[str] = None, web_app: Optional[Dict] = None,
                   login_url: Optional[Dict] = None, switch_inline_query: Optional[str] = None,
                   switch_inline_query_current_chat: Optional[str] = None,
                   callback_game: Optional[Dict] = None, pay: bool = False) -> 'InlineKeyboardBuilder':
        """
        Добавить кнопку в текущий ряд
        
        Args:
            text: Текст кнопки
            callback_data: Данные для callback
            url: URL для кнопки
            web_app: Web app данные
            login_url: URL для авторизации
            switch_inline_query: Inline query для переключения
            switch_inline_query_current_chat: Inline query для текущего чата
            callback_game: Данные для игры
            pay: Является ли кнопка платёжной
            
        Returns:
            Self для цепочки вызовов
        """
        button: Dict[str, Any] = {"text": text}
        
        if callback_data:
            button["callback_data"] = callback_data
        elif url:
            button["url"] = url
        elif web_app:
            button["web_app"] = web_app
        elif login_url:
            button["login_url"] = login_url
        elif switch_inline_query:
            button["switch_inline_query"] = switch_inline_query
        elif switch_inline_query_current_chat:
            button["switch_inline_query_current_chat"] = switch_inline_query_current_chat
        elif callback_game:
            button["callback_game"] = callback_game
        elif pay:
            button["pay"] = pay
        
        self.current_row.append(button)
        return self
    
    def row(self) -> 'InlineKeyboardBuilder':
        """
        Завершить текущий ряд и начать новый
        
        Returns:
            Self для цепочки вызовов
        """
        if self.current_row:
            self.buttons.append(self.current_row)
            self.current_row = []
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Построить клавиатуру
        
        Returns:
            Словарь с клавиатурой для Telegram API
        """
        if self.current_row:
            self.buttons.append(self.current_row)
            self.current_row = []
        return {"inline_keyboard": self.buttons}
    
    def clear(self) -> 'InlineKeyboardBuilder':
        """Очистить клавиатуру"""
        self.buttons = []
        self.current_row = []
        return self


class ReplyKeyboardBuilder:
    """Построитель reply клавиатур"""
    
    def __init__(self, resize_keyboard: bool = True, one_time_keyboard: bool = False,
                 input_field_placeholder: Optional[str] = None, selective: bool = False):
        """
        Инициализация построителя
        
        Args:
            resize_keyboard: Изменять ли размер клавиатуры
            one_time_keyboard: Одноразовая ли клавиатура
            input_field_placeholder: Плейсхолдер для поля ввода
            selective: Показывать ли клавиатуру только определённым пользователям
        """
        self.buttons: List[List[Dict[str, Any]]] = []
        self.current_row: List[Dict[str, Any]] = []
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.input_field_placeholder = input_field_placeholder
        self.selective = selective
    
    def add_button(self, text: str, request_contact: bool = False,
                   request_location: bool = False,
                   request_poll: Optional[Dict[str, str]] = None,
                   web_app: Optional[Dict] = None) -> 'ReplyKeyboardBuilder':
        """
        Добавить кнопку в текущий ряд
        
        Args:
            text: Текст кнопки
            request_contact: Запрашивать ли контакт
            request_location: Запрашивать ли местоположение
            request_poll: Запрашивать ли опрос
            web_app: Web app данные
            
        Returns:
            Self для цепочки вызовов
        """
        button: Dict[str, Any] = {"text": text}
        
        if request_contact:
            button["request_contact"] = True
        elif request_location:
            button["request_location"] = True
        elif request_poll:
            button["request_poll"] = request_poll
        elif web_app:
            button["web_app"] = web_app
        
        self.current_row.append(button)
        return self
    
    def row(self) -> 'ReplyKeyboardBuilder':
        """
        Завершить текущий ряд и начать новый
        
        Returns:
            Self для цепочки вызовов
        """
        if self.current_row:
            self.buttons.append(self.current_row)
            self.current_row = []
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Построить клавиатуру
        
        Returns:
            Словарь с клавиатурой для Telegram API
        """
        if self.current_row:
            self.buttons.append(self.current_row)
            self.current_row = []
        
        keyboard = {
            "keyboard": self.buttons,
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.one_time_keyboard,
            "selective": self.selective,
        }
        
        if self.input_field_placeholder:
            keyboard["input_field_placeholder"] = self.input_field_placeholder
        
        return keyboard
    
    def remove(self) -> Dict[str, Any]:
        """
        Удалить клавиатуру
        
        Returns:
            Словарь для удаления клавиатуры
        """
        return {"remove_keyboard": True, "selective": self.selective}
    
    def clear(self) -> 'ReplyKeyboardBuilder':
        """Очистить клавиатуру"""
        self.buttons = []
        self.current_row = []
        return self

