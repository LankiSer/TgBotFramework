# TgFramework

Полнофункциональный фреймворк для разработки Telegram ботов с использованием стандартного Telegram Bot API в режиме polling и встроенной базой данных SQLite.

## Содержание

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Документация API](#документация-api)
  - [Класс Bot](#класс-bot)
  - [Класс Database](#класс-database)
  - [Класс Quiz](#класс-quiz)
  - [Класс QuizQuestion](#класс-quizquestion)
  - [InlineKeyboardBuilder](#inlinekeyboardbuilder)
  - [ReplyKeyboardBuilder](#replykeyboardbuilder)
  - [StateMachine](#statemachine)
  - [Middleware](#middleware)
  - [Утилиты](#утилиты)

## Установка

### Через PyPI

```bash
pip install tgframework-bot
```

### Из исходников

```bash
pip install -r requirements.txt
```

Или установите как пакет:

```bash
pip install -e .
```

## Быстрый старт

```python
from tgframework import Bot

bot = Bot(token="YOUR_BOT_TOKEN_HERE")

@bot.register_command("start")
async def start_command(update, context):
    await bot.send_message(
        context["chat"]["id"],
        "Привет! Я бот на TgFramework."
    )

bot.run()
```

## Документация API

### Класс Bot

Основной класс для работы с Telegram ботом. Поддерживает polling для получения обновлений от Telegram.

#### `__init__(token: str, db_path: str = "bot.db")`

Инициализирует бота.

**Параметры:**
- `token` (str): Токен бота от @BotFather
- `db_path` (str, опционально): Путь к файлу базы данных. По умолчанию "bot.db"

**Пример:**
```python
bot = Bot(token="123456:ABC-DEF", db_path="my_bot.db")
```

#### `send_message(chat_id: int, text: str, reply_markup: Optional[Dict] = None, parse_mode: Optional[str] = None, reply_to_message_id: Optional[int] = None, **kwargs) -> Dict[str, Any]`

Отправляет текстовое сообщение в чат.

**Параметры:**
- `chat_id` (int): ID чата для отправки сообщения
- `text` (str): Текст сообщения
- `reply_markup` (Dict, опционально): Клавиатура для прикрепления к сообщению
- `parse_mode` (str, опционально): Режим парсинга текста ("HTML", "Markdown", "MarkdownV2")
- `reply_to_message_id` (int, опционально): ID сообщения, на которое отвечаем
- `**kwargs`: Дополнительные параметры Telegram Bot API

**Возвращает:**
- `Dict[str, Any]`: Отправленное сообщение

**Пример:**
```python
await bot.send_message(
    chat_id=123456,
    text="Привет!",
    parse_mode="HTML"
)
```

#### `edit_message_text(chat_id: int, message_id: int, text: str, reply_markup: Optional[Dict] = None, parse_mode: Optional[str] = None, **kwargs) -> Dict[str, Any]`

Редактирует текст существующего сообщения.

**Параметры:**
- `chat_id` (int): ID чата
- `message_id` (int): ID сообщения для редактирования
- `text` (str): Новый текст сообщения
- `reply_markup` (Dict, опционально): Новая клавиатура
- `parse_mode` (str, опционально): Режим парсинга
- `**kwargs`: Дополнительные параметры

**Возвращает:**
- `Dict[str, Any]`: Отредактированное сообщение

**Пример:**
```python
await bot.edit_message_text(
    chat_id=123456,
    message_id=789,
    text="Обновленный текст"
)
```

#### `delete_message(chat_id: int, message_id: int) -> bool`

Удаляет сообщение из чата.

**Параметры:**
- `chat_id` (int): ID чата
- `message_id` (int): ID сообщения для удаления

**Возвращает:**
- `bool`: True если успешно удалено

**Пример:**
```python
await bot.delete_message(chat_id=123456, message_id=789)
```

#### `answer_callback_query(callback_query_id: str, text: Optional[str] = None, show_alert: bool = False, **kwargs) -> bool`

Отвечает на callback query.

**Параметры:**
- `callback_query_id` (str): ID callback query
- `text` (str, опционально): Текст ответа
- `show_alert` (bool, опционально): Показать ли alert вместо уведомления. По умолчанию False
- `**kwargs`: Дополнительные параметры

**Возвращает:**
- `bool`: True если успешно

**Пример:**
```python
await bot.answer_callback_query(
    callback_query_id="123",
    text="Кнопка нажата!"
)
```

#### `register_command(command: str = None, handler: Callable = None, description: Optional[str] = None)`

Регистрирует обработчик команды. Может использоваться как декоратор или как обычный метод.

**Параметры:**
- `command` (str): Название команды без "/"
- `handler` (Callable, опционально): Функция-обработчик (если используется как декоратор)
- `description` (str, опционально): Описание команды

**Пример использования как декоратора:**
```python
@bot.register_command("start")
async def start_command(update, context):
    await bot.send_message(context["chat"]["id"], "Привет!")
```

**Пример использования как метода:**
```python
async def start_handler(update, context):
    await bot.send_message(context["chat"]["id"], "Привет!")

bot.register_command("start", start_handler, "Начать работу")
```

#### `register_callback(pattern: str = None, handler: Callable = None)`

Регистрирует обработчик callback query. Может использоваться как декоратор или как обычный метод.

**Параметры:**
- `pattern` (str): Паттерн для callback_data (callback должен начинаться с этого паттерна)
- `handler` (Callable, опционально): Функция-обработчик (если используется как декоратор)

**Пример:**
```python
@bot.register_callback("button_")
async def button_handler(update, context):
    callback_data = context["callback_data"]
    await bot.answer_callback_query(context["callback_query"]["id"])
```

#### `register_message_handler(handler: Callable = None, filters: Optional[Callable] = None)`

Регистрирует обработчик текстовых сообщений. Может использоваться как декоратор или как обычный метод.

**Параметры:**
- `handler` (Callable, опционально): Функция-обработчик (если используется как декоратор)
- `filters` (Callable, опционально): Функция-фильтр для проверки сообщения. Должна возвращать True/False

**Пример:**
```python
@bot.register_message_handler(
    filters=lambda u: u.get("message", {}).get("text")
)
async def text_handler(update, context):
    text = context["text"]
    await bot.send_message(context["chat"]["id"], f"Вы написали: {text}")
```

#### `start_polling()`

Асинхронно запускает polling для получения обновлений.

**Пример:**
```python
await bot.start_polling()
```

#### `stop()`

Останавливает бота и закрывает соединения.

**Пример:**
```python
await bot.stop()
```

#### `run()`

Синхронно запускает бота (блокирующий метод).

**Пример:**
```python
bot.run()
```

### Класс Database

Класс для работы с SQLite базой данных. Автоматически создает необходимые таблицы.

#### `__init__(db_path: str = "bot.db")`

Инициализирует базу данных и создает таблицы.

**Параметры:**
- `db_path` (str): Путь к файлу базы данных. По умолчанию "bot.db"

**Создаваемые таблицы:**
- `users` - информация о пользователях
- `chats` - информация о чатах
- `messages` - история сообщений
- `user_states` - состояния пользователей
- `quizzes` - квизы

#### `add_user(user_id: int, username: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, language_code: Optional[str] = None, is_bot: bool = False, is_admin: bool = False)`

Добавляет или обновляет информацию о пользователе.

**Параметры:**
- `user_id` (int): ID пользователя
- `username` (str, опционально): Username пользователя
- `first_name` (str, опционально): Имя пользователя
- `last_name` (str, опционально): Фамилия пользователя
- `language_code` (str, опционально): Код языка пользователя
- `is_bot` (bool, опционально): Является ли пользователь ботом
- `is_admin` (bool, опционально): Является ли пользователь администратором

**Пример:**
```python
db.add_user(123456, username="john_doe", first_name="John", is_admin=True)
```

#### `get_user(user_id: int) -> Optional[sqlite3.Row]`

Получает информацию о пользователе.

**Параметры:**
- `user_id` (int): ID пользователя

**Возвращает:**
- `Optional[sqlite3.Row]`: Строка с данными пользователя или None

**Пример:**
```python
user = db.get_user(123456)
if user:
    print(user["first_name"])
```

#### `set_user_state(user_id: int, state: str, data: Optional[str] = None)`

Устанавливает состояние пользователя.

**Параметры:**
- `user_id` (int): ID пользователя
- `state` (str): Состояние
- `data` (str, опционально): Дополнительные данные в формате JSON

**Пример:**
```python
db.set_user_state(123456, "waiting_for_name")
```

#### `get_user_state(user_id: int) -> Optional[sqlite3.Row]`

Получает состояние пользователя.

**Параметры:**
- `user_id` (int): ID пользователя

**Возвращает:**
- `Optional[sqlite3.Row]`: Данные состояния или None

#### `clear_user_state(user_id: int)`

Очищает состояние пользователя.

**Параметры:**
- `user_id` (int): ID пользователя

#### `add_chat(chat_id: int, chat_type: str, title: Optional[str] = None, username: Optional[str] = None)`

Добавляет или обновляет информацию о чате.

**Параметры:**
- `chat_id` (int): ID чата
- `chat_type` (str): Тип чата ("private", "group", "supergroup", "channel")
- `title` (str, опционально): Название чата
- `username` (str, опционально): Username чата

#### `save_message(message_id: int, chat_id: int, user_id: int, text: Optional[str])`

Сохраняет сообщение в базу данных.

**Параметры:**
- `message_id` (int): ID сообщения
- `chat_id` (int): ID чата
- `user_id` (int): ID пользователя
- `text` (str, опционально): Текст сообщения

#### `execute(query: str, params: Tuple = ()) -> sqlite3.Cursor`

Выполняет произвольный SQL запрос.

**Параметры:**
- `query` (str): SQL запрос
- `params` (Tuple): Параметры запроса

**Возвращает:**
- `sqlite3.Cursor`: Курсор с результатами

#### `fetchone(query: str, params: Tuple = ()) -> Optional[sqlite3.Row]`

Выполняет запрос и возвращает одну строку.

**Параметры:**
- `query` (str): SQL запрос
- `params` (Tuple): Параметры запроса

**Возвращает:**
- `Optional[sqlite3.Row]`: Одна строка результата или None

#### `fetchall(query: str, params: Tuple = ()) -> List[sqlite3.Row]`

Выполняет запрос и возвращает все строки.

**Параметры:**
- `query` (str): SQL запрос
- `params` (Tuple): Параметры запроса

**Возвращает:**
- `List[sqlite3.Row]`: Список всех строк результата

#### `set_admin(user_id: int, is_admin: bool = True)`

Устанавливает статус администратора для пользователя.

**Параметры:**
- `user_id` (int): ID пользователя
- `is_admin` (bool, опционально): Установить статус администратора. По умолчанию True

**Пример:**
```python
db.set_admin(123456, is_admin=True)  # Дать права администратора
db.set_admin(123456, is_admin=False)  # Убрать права администратора
```

#### `is_admin(user_id: int) -> bool`

Проверяет, является ли пользователь администратором.

**Параметры:**
- `user_id` (int): ID пользователя

**Возвращает:**
- `bool`: True если пользователь является администратором

**Пример:**
```python
if db.is_admin(123456):
    print("Пользователь является администратором")
```

#### `get_all_admins() -> List[sqlite3.Row]`

Получает список всех администраторов.

**Возвращает:**
- `List[sqlite3.Row]`: Список всех администраторов

**Пример:**
```python
admins = db.get_all_admins()
for admin in admins:
    print(admin["first_name"])
```

#### `get_all_users(limit: Optional[int] = None) -> List[sqlite3.Row]`

Получает список всех пользователей.

**Параметры:**
- `limit` (int, опционально): Максимальное количество пользователей

**Возвращает:**
- `List[sqlite3.Row]`: Список пользователей

**Пример:**
```python
users = db.get_all_users(limit=10)  # Последние 10 пользователей
```

#### `get_user_count() -> int`

Получает общее количество пользователей в базе данных.

**Возвращает:**
- `int`: Количество пользователей

**Пример:**
```python
count = db.get_user_count()
print(f"Всего пользователей: {count}")
```

#### `close()`

Закрывает соединение с базой данных.

### Класс Quiz

Класс для создания и управления квизами.

#### `__init__(db, user_id: int, title: str = "Квиз")`

Инициализирует квиз.

**Параметры:**
- `db`: Экземпляр базы данных
- `user_id` (int): ID пользователя
- `title` (str, опционально): Название квиза. По умолчанию "Квиз"

#### `add_question(question: QuizQuestion)`

Добавляет вопрос в квиз.

**Параметры:**
- `question` (QuizQuestion): Вопрос для добавления

#### `add_questions(questions: List[QuizQuestion])`

Добавляет несколько вопросов в квиз.

**Параметры:**
- `questions` (List[QuizQuestion]): Список вопросов

#### `save() -> int`

Сохраняет квиз в базу данных.

**Возвращает:**
- `int`: ID сохраненного квиза

#### `load(quiz_id: int)`

Загружает квиз из базы данных.

**Параметры:**
- `quiz_id` (int): ID квиза

#### `get_current_question() -> Optional[QuizQuestion]`

Получает текущий вопрос квиза.

**Возвращает:**
- `Optional[QuizQuestion]`: Текущий вопрос или None

#### `answer(answer_index: int) -> bool`

Обрабатывает ответ пользователя на текущий вопрос.

**Параметры:**
- `answer_index` (int): Индекс выбранного ответа

**Возвращает:**
- `bool`: True если ответ правильный, False если неправильный

#### `next_question() -> Optional[QuizQuestion]`

Переходит к следующему вопросу.

**Возвращает:**
- `Optional[QuizQuestion]`: Следующий вопрос или None

#### `is_finished() -> bool`

Проверяет, завершен ли квиз.

**Возвращает:**
- `bool`: True если квиз завершен

#### `get_results() -> Dict[str, Any]`

Получает результаты квиза.

**Возвращает:**
- `Dict[str, Any]`: Словарь с результатами:
  - `score` (int): Количество правильных ответов
  - `total` (int): Общее количество вопросов
  - `percentage` (float): Процент правильных ответов
  - `correct` (int): Количество правильных ответов
  - `incorrect` (int): Количество неправильных ответов

#### `finish()`

Завершает квиз (меняет статус на "finished").

#### `get_user_active_quiz(db, user_id: int) -> Optional['Quiz']`

Статический метод. Получает активный квиз пользователя.

**Параметры:**
- `db`: Экземпляр базы данных
- `user_id` (int): ID пользователя

**Возвращает:**
- `Optional[Quiz]`: Активный квиз или None

**Пример:**
```python
quiz = Quiz.get_user_active_quiz(db, user_id=123456)
```

### Класс QuizQuestion

Dataclass для представления вопроса квиза.

#### Поля

- `question` (str): Текст вопроса
- `options` (List[str]): Список вариантов ответа
- `correct_answer` (int): Индекс правильного ответа в списке options
- `explanation` (Optional[str]): Объяснение правильного ответа

**Пример:**
```python
question = QuizQuestion(
    question="Что такое Python?",
    options=["Змея", "Язык программирования", "Фреймворк"],
    correct_answer=1,
    explanation="Python - это высокоуровневый язык программирования."
)
```

### InlineKeyboardBuilder

Класс для построения inline клавиатур.

#### `__init__()`

Создает новый построитель inline клавиатуры.

#### `add_button(text: str, callback_data: Optional[str] = None, url: Optional[str] = None, web_app: Optional[Dict] = None, login_url: Optional[Dict] = None, switch_inline_query: Optional[str] = None, switch_inline_query_current_chat: Optional[str] = None, callback_game: Optional[Dict] = None, pay: bool = False) -> 'InlineKeyboardBuilder'`

Добавляет кнопку в текущий ряд.

**Параметры:**
- `text` (str): Текст кнопки
- `callback_data` (str, опционально): Данные для callback
- `url` (str, опционально): URL для кнопки
- `web_app` (Dict, опционально): Web app данные
- `login_url` (Dict, опционально): URL для авторизации
- `switch_inline_query` (str, опционально): Inline query для переключения
- `switch_inline_query_current_chat` (str, опционально): Inline query для текущего чата
- `callback_game` (Dict, опционально): Данные для игры
- `pay` (bool, опционально): Является ли кнопка платёжной

**Возвращает:**
- `InlineKeyboardBuilder`: Self для цепочки вызовов

**Пример:**
```python
keyboard = InlineKeyboardBuilder()
keyboard.add_button("Кнопка 1", callback_data="btn1")
keyboard.add_button("Кнопка 2", callback_data="btn2")
keyboard.row()
keyboard.add_button("URL кнопка", url="https://example.com")
```

#### `row() -> 'InlineKeyboardBuilder'`

Завершает текущий ряд и начинает новый.

**Возвращает:**
- `InlineKeyboardBuilder`: Self для цепочки вызовов

#### `build() -> Dict[str, Any]`

Строит клавиатуру для использования в Telegram API.

**Возвращает:**
- `Dict[str, Any]`: Словарь с клавиатурой

**Пример:**
```python
keyboard = InlineKeyboardBuilder()
keyboard.add_button("Да", callback_data="yes")
keyboard.add_button("Нет", callback_data="no")
await bot.send_message(chat_id, "Выберите:", reply_markup=keyboard.build())
```

#### `clear() -> 'InlineKeyboardBuilder'`

Очищает клавиатуру.

**Возвращает:**
- `InlineKeyboardBuilder`: Self для цепочки вызовов

### ReplyKeyboardBuilder

Класс для построения reply клавиатур.

#### `__init__(resize_keyboard: bool = True, one_time_keyboard: bool = False, input_field_placeholder: Optional[str] = None, selective: bool = False)`

Создает новый построитель reply клавиатуры.

**Параметры:**
- `resize_keyboard` (bool, опционально): Изменять ли размер клавиатуры. По умолчанию True
- `one_time_keyboard` (bool, опционально): Одноразовая ли клавиатура. По умолчанию False
- `input_field_placeholder` (str, опционально): Плейсхолдер для поля ввода
- `selective` (bool, опционально): Показывать ли клавиатуру только определённым пользователям. По умолчанию False

#### `add_button(text: str, request_contact: bool = False, request_location: bool = False, request_poll: Optional[Dict[str, str]] = None, web_app: Optional[Dict] = None) -> 'ReplyKeyboardBuilder'`

Добавляет кнопку в текущий ряд.

**Параметры:**
- `text` (str): Текст кнопки
- `request_contact` (bool, опционально): Запрашивать ли контакт
- `request_location` (bool, опционально): Запрашивать ли местоположение
- `request_poll` (Dict[str, str], опционально): Запрашивать ли опрос
- `web_app` (Dict, опционально): Web app данные

**Возвращает:**
- `ReplyKeyboardBuilder`: Self для цепочки вызовов

#### `row() -> 'ReplyKeyboardBuilder'`

Завершает текущий ряд и начинает новый.

**Возвращает:**
- `ReplyKeyboardBuilder`: Self для цепочки вызовов

#### `build() -> Dict[str, Any]`

Строит клавиатуру для использования в Telegram API.

**Возвращает:**
- `Dict[str, Any]`: Словарь с клавиатурой

#### `remove() -> Dict[str, Any]`

Возвращает словарь для удаления клавиатуры.

**Возвращает:**
- `Dict[str, Any]`: Словарь для удаления клавиатуры

**Пример:**
```python
keyboard = ReplyKeyboardBuilder()
await bot.send_message(chat_id, "Клавиатура удалена", reply_markup=keyboard.remove())
```

#### `clear() -> 'ReplyKeyboardBuilder'`

Очищает клавиатуру.

**Возвращает:**
- `ReplyKeyboardBuilder`: Self для цепочки вызовов

### StateMachine

Класс для управления состояниями пользователей.

#### `__init__(db)`

Инициализирует машину состояний.

**Параметры:**
- `db`: Экземпляр базы данных

#### `set_state(user_id: int, state: str, data: Optional[Dict] = None)`

Устанавливает состояние пользователя.

**Параметры:**
- `user_id` (int): ID пользователя
- `state` (str): Состояние
- `data` (Dict, опционально): Дополнительные данные

**Пример:**
```python
state_machine.set_state(user_id=123456, state="waiting_for_name", data={"step": 1})
```

#### `get_state(user_id: int) -> Optional[str]`

Получает состояние пользователя.

**Параметры:**
- `user_id` (int): ID пользователя

**Возвращает:**
- `Optional[str]`: Состояние пользователя или None

#### `get_state_data(user_id: int) -> Optional[Dict]`

Получает данные состояния пользователя.

**Параметры:**
- `user_id` (int): ID пользователя

**Возвращает:**
- `Optional[Dict]`: Данные состояния или None

#### `clear_state(user_id: int)`

Очищает состояние пользователя.

**Параметры:**
- `user_id` (int): ID пользователя

#### `register_state_handler(state: str, handler: Callable)`

Регистрирует обработчик состояния.

**Параметры:**
- `state` (str): Состояние
- `handler` (Callable): Функция-обработчик

#### `get_state_handler(state: str) -> Optional[Callable]`

Получает обработчик состояния.

**Параметры:**
- `state` (str): Состояние

**Возвращает:**
- `Optional[Callable]`: Обработчик или None

### Middleware

Система middleware для обработки обновлений.

#### Класс Middleware

Базовый абстрактный класс для создания middleware.

##### `process(update: Dict[str, Any], context: Dict[str, Any]) -> bool`

Абстрактный метод для обработки update.

**Параметры:**
- `update` (Dict[str, Any]): Update от Telegram
- `context` (Dict[str, Any]): Контекст обработки

**Возвращает:**
- `bool`: True если продолжить обработку, False если остановить

**Пример:**
```python
from tgframework import Middleware

class MyMiddleware(Middleware):
    async def process(self, update, context):
        # Ваша логика обработки
        return True  # Продолжить обработку
```

#### Класс MiddlewareManager

Менеджер для управления middleware.

##### `add(middleware: Middleware)`

Добавляет middleware.

**Параметры:**
- `middleware` (Middleware): Middleware для добавления

**Пример:**
```python
bot.middleware_manager.add(MyMiddleware())
```

##### `process(update: Dict[str, Any], context: Dict[str, Any]) -> bool`

Обрабатывает update через все middleware.

**Параметры:**
- `update` (Dict[str, Any]): Update от Telegram
- `context` (Dict[str, Any]): Контекст обработки

**Возвращает:**
- `bool`: True если продолжить обработку, False если остановить

### Утилиты

Модуль `utils` содержит вспомогательные функции.

#### `get_user_info(user: Dict[str, Any]) -> Dict[str, Any]`

Получает информацию о пользователе в удобном формате.

**Параметры:**
- `user` (Dict[str, Any]): Словарь с данными пользователя из Telegram API

**Возвращает:**
- `Dict[str, Any]`: Словарь с информацией:
  - `id` (int): ID пользователя
  - `username` (str): Username
  - `first_name` (str): Имя
  - `last_name` (str): Фамилия
  - `full_name` (str): Полное имя
  - `language_code` (str): Код языка
  - `is_bot` (bool): Является ли ботом
  - `is_premium` (bool): Является ли премиум пользователем

**Пример:**
```python
from tgframework import get_user_info

user_info = get_user_info(context["user"])
print(user_info["full_name"])
```

#### `get_chat_info(chat: Dict[str, Any]) -> Dict[str, Any]`

Получает информацию о чате в удобном формате.

**Параметры:**
- `chat` (Dict[str, Any]): Словарь с данными чата из Telegram API

**Возвращает:**
- `Dict[str, Any]`: Словарь с информацией:
  - `id` (int): ID чата
  - `type` (str): Тип чата
  - `title` (str): Название чата
  - `username` (str): Username чата
  - `first_name` (str): Имя (для приватных чатов)
  - `last_name` (str): Фамилия (для приватных чатов)

#### `format_text(text: str, **kwargs) -> str`

Форматирует текст с подстановкой переменных.

**Параметры:**
- `text` (str): Текст с плейсхолдерами {variable_name}
- `**kwargs`: Переменные для подстановки

**Возвращает:**
- `str`: Отформатированный текст

**Пример:**
```python
from tgframework import format_text

text = format_text("Привет, {name}!", name="Иван")
# Результат: "Привет, Иван!"
```

#### `escape_markdown(text: str) -> str`

Экранирует специальные символы для Markdown.

**Параметры:**
- `text` (str): Исходный текст

**Возвращает:**
- `str`: Экранированный текст

#### `escape_html(text: str) -> str`

Экранирует специальные символы для HTML.

**Параметры:**
- `text` (str): Исходный текст

**Возвращает:**
- `str`: Экранированный текст

#### `parse_command(text: str) -> tuple[str, str]`

Парсит команду из текста.

**Параметры:**
- `text` (str): Текст команды (например, "/start arg1 arg2")

**Возвращает:**
- `tuple[str, str]`: Кортеж (команда, аргументы)

**Пример:**
```python
from tgframework import parse_command

command, args = parse_command("/start hello world")
# command = "start"
# args = "hello world"
```

## Новые возможности 2.0

### Webhook поддержка

```python
# Запуск в режиме webhook
await bot.start_webhook(
    host="0.0.0.0",
    port=8080,
    path="/webhook",
    secret_token="your_secret_token"
)
```

### FSM (Finite State Machine)

```python
from tgframework import FSMState, StatesGroup, FSMContext, state

class MyStates(StatesGroup):
    waiting_for_name = FSMState()
    waiting_for_age = FSMState()

@state(MyStates.waiting_for_name)
async def handle_name(update, context):
    fsm = FSMContext(bot.state_machine, context["user"]["id"], context["chat"]["id"])
    await fsm.set_state(MyStates.waiting_for_age)
    await fsm.update_data(name=context["text"])
```

### Готовые фильтры

```python
from tgframework import Filters

# Фильтр для фото
@bot.register_message_handler(filters=Filters.Photo())
async def photo_handler(update, context):
    ...

# Комбинация фильтров
@bot.register_message_handler(filters=Filters.Text() & Filters.PrivateChat())
async def private_text_handler(update, context):
    ...
```

### Pagination

```python
from tgframework import PaginationKeyboard

items = ["Элемент 1", "Элемент 2", ...]
pagination = PaginationKeyboard(
    items=items,
    items_per_page=5,
    callback_prefix="page_"
)

keyboard = pagination.build(0)  # Первая страница
await bot.send_message(chat_id, "Список:", reply_markup=keyboard)
```

### Обработка ошибок

```python
@bot.register_error_handler
async def error_handler(error, context):
    print(f"Ошибка: {error}")
    # Ваша логика обработки
```

## Примеры

В папке `examples/` находятся примеры ботов:

- `simple_bot.py` - простой бот с базовыми командами
- `quiz_bot.py` - бот с полноценной системой квизов
- `admin_bot.py` - бот с регистрацией пользователей и админкой
- `advanced_bot.py` - продвинутый пример с FSM, фильтрами, pagination и обработкой ошибок

## Структура проекта

```
tgframework/
├── __init__.py          # Основной модуль
├── bot.py               # Класс бота (polling и webhook)
├── database.py          # Работа с базой данных
├── handlers.py          # Обработчики
├── quiz.py              # Система квизов
├── keyboards.py         # Построители клавиатур
├── state.py             # Управление состояниями
├── fsm.py               # FSM система (как в aiogram)
├── filters.py           # Готовые фильтры
├── pagination.py        # Pagination для клавиатур
├── rate_limiter.py      # Rate limiting защита
├── middleware.py        # Middleware система
└── utils.py             # Утилиты

examples/
├── simple_bot.py        # Простой пример
├── quiz_bot.py          # Пример с квизами
├── admin_bot.py         # Пример с регистрацией и админкой
└── advanced_bot.py      # Продвинутый пример (FSM, фильтры, pagination)

requirements.txt
setup.py
README.md
```

## Сравнение с другими библиотеками

TgFramework создан как простая и удобная альтернатива существующим библиотекам для создания Telegram ботов. Ниже представлено сравнение с популярными решениями:

### TgFramework vs python-telegram-bot

**Преимущества TgFramework:**
- Встроенная база данных SQLite с автоматическим управлением таблицами
- Готовая система квизов
- Более простой и интуитивный API для быстрого старта
- Встроенная система состояний пользователей
- Меньше зависимостей (только aiohttp)
- Простая регистрация обработчиков через декораторы

**Недостатки TgFramework:**
- Меньше документации и примеров (новый проект)
- Ограниченная поддержка Telegram Bot API (базовые методы)
- Только polling режим (нет webhook)

**Когда использовать TgFramework:**
- Для быстрого создания простых ботов
- Когда нужна встроенная база данных
- Для проектов с квизами и опросами
- Когда важна простота использования

**Когда использовать python-telegram-bot:**
- Для сложных проектов с полной поддержкой Telegram Bot API
- Когда нужен webhook вместо polling
- Для enterprise проектов с требованием стабильности

### TgFramework vs aiogram

**Преимущества TgFramework 2.0:**
- Встроенная база данных SQLite с готовыми таблицами (пользователи, чаты, сообщения, состояния, квизы)
- Система квизов из коробки - полнофункциональная система для создания тестов и опросов
- FSM (Finite State Machine) - полноценная система состояний как в aiogram с декораторами
- Готовые фильтры (Filters) - удобные фильтры для обработчиков с операторами &, |, ~
- Pagination для клавиатур - встроенная навигация по страницам
- Rate limiting защита - автоматическая защита от превышения лимитов Telegram API
- Webhook поддержка - работает как polling, так и webhook режим
- Улучшенная обработка ошибок - глобальные обработчики ошибок с логированием
- Встроенная админка по ID пользователей
- Retry механизм - автоматические повторы при ошибках API
- Логирование - встроенная система логирования
- Меньше зависимостей - только aiohttp (vs множество зависимостей в aiogram)
- Более простая архитектура для начинающих
- Меньше абстракций, более понятный код

**Недостатки TgFramework:**
- Новый проект - меньше сообщества и примеров
- Не все методы Telegram Bot API реализованы (но все основные есть)
- Меньше сторонних расширений и плагинов

**Когда использовать TgFramework:**
- Для быстрого создания ботов с минимальной настройкой
- Когда нужна встроенная база данных без дополнительной настройки
- Для ботов с квизами и опросами
- Когда важна простота и минимум зависимостей
- Для обучения и экспериментов
- Для production проектов с базовым и средним функционалом

**Когда использовать aiogram:**
- Для очень сложных ботов с множеством интеграций
- Когда нужны все методы Telegram Bot API без исключений
- Для проектов с большой командой разработчиков, знакомых с aiogram
- Когда нужны сторонние расширения и плагины

### TgFramework vs Telethon

**Преимущества TgFramework:**
- Работает с Bot API (проще получить токен)
- Встроенная база данных
- Готовая система квизов и админки
- Синхронный и асинхронный API
- Проще для начинающих

**Недостатки TgFramework:**
- Работает только с Bot API (не Client API)
- Меньше возможностей для автоматизации

**Когда использовать TgFramework:**
- Для создания обычных Telegram ботов
- Когда не нужен Client API функционал

**Когда использовать Telethon:**
- Для работы с Telegram Client API
- Для автоматизации личных аккаунтов
- Для сложных сценариев взаимодействия с Telegram

### Итоговое сравнение

| Функция | TgFramework 2.0 | python-telegram-bot | aiogram | Telethon |
|---------|-----------------|---------------------|---------|----------|
| База данных из коробки | Да (SQLite) | Нет | Нет | Нет |
| Система квизов | Да | Нет | Нет | Нет |
| FSM (состояния) | Да | Частично | Да | Нет |
| Готовые фильтры | Да | Частично | Да | Нет |
| Pagination | Да | Нет | Нет | Нет |
| Rate limiting | Да | Частично | Частично | Нет |
| Webhook поддержка | Да | Да | Да | Да |
| Обработка ошибок | Да (улучшенная) | Да | Да | Да |
| Retry механизм | Да | Да | Частично | Нет |
| Логирование | Да | Да | Да | Да |
| Режим работы | Polling/Webhook | Polling/Webhook | Polling/Webhook | Client/Bot API |
| Простота использования | Высокая | Средняя | Средняя | Низкая |
| Поддержка Bot API | Основные методы | Полная | Полная | Полная |
| Зависимости | Минимум (aiohttp) | Средние | Средние | Средние |
| Админка из коробки | Да | Нет | Нет | Нет |
| Документация | Хорошая | Отличная | Хорошая | Хорошая |
| Сообщество | Растущее | Большое | Большое | Большое |

### Вывод

**TgFramework 2.0 теперь лучше чем aiogram в следующих аспектах:**

1. **Встроенная база данных** - не нужно настраивать SQLAlchemy или другие ORM
2. **Система квизов** - готовая система из коробки, в aiogram нужно писать с нуля
3. **Админка по ID** - готовая система управления администраторами
4. **Pagination** - встроенная навигация по страницам
5. **Меньше зависимостей** - только aiohttp vs множество в aiogram
6. **Проще для начинающих** - более понятный и интуитивный API
7. **Rate limiting из коробки** - автоматическая защита от лимитов
8. **Улучшенная обработка ошибок** - глобальные обработчики с retry

**TgFramework 2.0 идеально подходит для:**
- Быстрого создания ботов с минимальной настройкой
- Проектов, требующих встроенную базу данных
- Ботов с квизами и опросами
- Проектов, где важна простота и минимум зависимостей
- Production ботов с базовым и средним функционалом
- Обучения и экспериментов

**Когда стоит рассмотреть aiogram:**
- Если команда уже знакома с aiogram
- Для очень сложных проектов с множеством интеграций
- Когда нужны все методы Telegram Bot API без исключений

## Лицензия

MIT License

## Авторы

TgFramework Team
