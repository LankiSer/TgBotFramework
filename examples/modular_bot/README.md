# Пример модульного бота

Этот пример демонстрирует правильную структуру модульного бота с разделением на файлы.

## Структура проекта

```
modular_bot/
├── config.py          # Единственный экземпляр бота
├── main.py            # Точка входа, запускает бота
├── app/
│   ├── __init__.py    # Пакет app
│   ├── handlers.py    # Обработчики команд и callback
│   └── keyboards.py   # Клавиатуры
└── README.md          # Эта документация
```

## Как использовать

1. Скопируйте папку `modular_bot` в свой проект
2. Откройте `config.py` и замените `YOUR_BOT_TOKEN_HERE` на токен вашего бота
3. Запустите:

```bash
python main.py
```

## Особенности

### 1. Единственный экземпляр бота (config.py)

Все обработчики импортируют один и тот же экземпляр бота из `config.py`:

```python
# config.py
from tgframework import Bot
bot = Bot(token="YOUR_BOT_TOKEN_HERE")
```

### 2. Разделение на модули

- **handlers.py** - все обработчики команд и callback
- **keyboards.py** - все клавиатуры
- **main.py** - только точка входа

### 3. Правильный порядок импортов

В `main.py`:
1. Сначала импортируем `bot` из `config`
2. Затем импортируем `handlers`, которые используют `bot`

```python
from config import bot
from app import handlers  # Это зарегистрирует все обработчики
```

### 4. Использование в handlers.py

Все обработчики импортируют `bot` из `config`:

```python
from config import bot

@bot.register_command("start")
async def start(update, context):
    # ...
```

## Доступные команды

- `/start` - Начать работу с ботом (регистрация)
- `/help` - Показать справку
- `/info` - Информация о пользователе
- `/menu` - Главное меню

## Обработчики callback

- `register_confirm` - Подтверждение регистрации
- `register_cancel` - Отмена регистрации
- `menu_profile` - Профиль пользователя
- `menu_help` - Помощь
- `menu_settings` - Настройки
- `button_yes` / `button_no` - Да/Нет

## Преимущества такой структуры

1. **Модульность** - каждый файл отвечает за свою область
2. **Масштабируемость** - легко добавлять новые обработчики и клавиатуры
3. **Читаемость** - код организован логично
4. **Переиспользование** - клавиатуры можно использовать в разных местах
5. **Отсутствие циклических импортов** - правильный порядок импортов

## Как добавить новый обработчик

1. Откройте `app/handlers.py`
2. Добавьте новый обработчик:

```python
@bot.register_command("mycommand")
async def my_command(update, context):
    await bot.send_message(context["chat"]["id"], "Моя команда!")
```

3. Обработчик автоматически зарегистрируется при импорте `handlers`

## Как добавить новую клавиатуру

1. Откройте `app/keyboards.py`
2. Добавьте новую функцию:

```python
def my_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Кнопка 1", "button_1")
    keyboard.add_button("Кнопка 2", "button_2")
    return keyboard
```

3. Используйте в обработчиках:

```python
from app.keyboards import my_keyboard

@bot.register_command("keyboard")
async def keyboard_command(update, context):
    await bot.send_message(
        context["chat"]["id"],
        "Выберите:",
        reply_markup=my_keyboard().build()
    )
```

