"""
Клавиатуры для бота
"""

from tgframework import InlineKeyboardBuilder


def register_button():
    """Создать клавиатуру для регистрации"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Зарегистрироваться", "register_confirm")
    keyboard.add_button("Отмена", "register_cancel")
    return keyboard


def menu_keyboard():
    """Создать главное меню"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Профиль", "menu_profile")
    keyboard.add_button("Помощь", "menu_help")
    keyboard.row()
    keyboard.add_button("Настройки", "menu_settings")
    return keyboard


def yes_no_keyboard():
    """Создать клавиатуру Да/Нет"""
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Да", "button_yes")
    keyboard.add_button("Нет", "button_no")
    return keyboard

