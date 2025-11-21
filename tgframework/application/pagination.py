"""
Pagination для клавиатур (навигация по страницам)
"""

from typing import List, Dict, Any, Callable, Optional
from .keyboards import InlineKeyboardBuilder


class PaginationKeyboard:
    """Клавиатура с пагинацией"""
    
    def __init__(self, items: List[Any], items_per_page: int = 5,
                 callback_prefix: str = "page_", 
                 item_formatter: Optional[Callable[[Any], str]] = None):
        """
        Инициализация клавиатуры с пагинацией
        
        Args:
            items: Список элементов для отображения
            items_per_page: Количество элементов на странице
            callback_prefix: Префикс для callback_data
            item_formatter: Функция для форматирования элемента в текст кнопки
        """
        self.items = items
        self.items_per_page = items_per_page
        self.callback_prefix = callback_prefix
        self.item_formatter = item_formatter or (lambda x: str(x))
        self.total_pages = (len(items) + items_per_page - 1) // items_per_page if items else 1
    
    def build(self, current_page: int = 0) -> Dict[str, Any]:
        """
        Построить клавиатуру для страницы
        
        Args:
            current_page: Текущая страница (0-based)
            
        Returns:
            Словарь с клавиатурой
        """
        if current_page < 0:
            current_page = 0
        if current_page >= self.total_pages:
            current_page = self.total_pages - 1
        
        keyboard = InlineKeyboardBuilder()
        
        # Элементы текущей страницы
        start_idx = current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_items = self.items[start_idx:end_idx]
        
        for i, item in enumerate(page_items):
            idx = start_idx + i
            text = self.item_formatter(item)
            callback_data = f"{self.callback_prefix}item_{idx}"
            keyboard.add_button(text, callback_data=callback_data)
            keyboard.row()
        
        # Навигация
        nav_row = []
        
        if current_page > 0:
            nav_row.append(("◀ Назад", f"{self.callback_prefix}page_{current_page - 1}"))
        
        nav_row.append((f"Страница {current_page + 1}/{self.total_pages}", f"{self.callback_prefix}current"))
        
        if current_page < self.total_pages - 1:
            nav_row.append(("Вперед ▶", f"{self.callback_prefix}page_{current_page + 1}"))
        
        for text, callback_data in nav_row:
            keyboard.add_button(text, callback_data=callback_data)
        
        keyboard.row()
        
        return keyboard.build()
    
    def get_item(self, item_index: int) -> Optional[Any]:
        """Получить элемент по индексу"""
        if 0 <= item_index < len(self.items):
            return self.items[item_index]
        return None


class SimplePagination:
    """Простая пагинация для списков"""
    
    @staticmethod
    def build(items: List[Any], page: int, per_page: int,
              item_format: Callable[[Any], str],
              callback_prefix: str = "page_") -> Dict[str, Any]:
        """
        Построить клавиатуру с пагинацией
        
        Args:
            items: Список элементов
            page: Текущая страница (0-based)
            per_page: Элементов на странице
            item_format: Функция форматирования элемента
            callback_prefix: Префикс для callback
            
        Returns:
            Словарь с клавиатурой
        """
        pagination = PaginationKeyboard(
            items=items,
            items_per_page=per_page,
            callback_prefix=callback_prefix,
            item_formatter=item_format
        )
        return pagination.build(page)

