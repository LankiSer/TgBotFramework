"""
Точка входа - запускает бота
"""

from config import bot

# Импортируем обработчики ПОСЛЕ создания bot в config
# Это важно для работы декораторов
from app import handlers

if __name__ == "__main__":
    print("Запуск модульного бота...")
    print("Структура:")
    print("- config.py - экземпляр бота")
    print("- app/handlers.py - обработчики команд")
    print("- app/keyboards.py - клавиатуры")
    print("- main.py - точка входа")
    print()
    bot.run()

