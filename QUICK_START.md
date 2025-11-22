# Быстрый старт TgFramework 3.0

## 1. Установка

```bash
# Базовая установка (SQLite)
pip install tgframework-bot python-dotenv

# С PostgreSQL
pip install tgframework-bot python-dotenv psycopg2-binary
```

## 2. Создание проекта

```bash
tgframework create-project my_bot
cd my_bot
```

Структура проекта:

```
my_bot/
├── .env                    # Конфигурация
├── main.py                 # Точка входа
├── migrations/             # Миграции БД
│   └── __init__.py
├── app/
│   ├── __init__.py
│   ├── handlers/          # Обработчики
│   │   ├── __init__.py
│   │   └── start.py
│   ├── domain/            # DDD модели
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── services.py
│   └── web/               # Веб-контроллеры
│       ├── __init__.py
│       └── controllers.py
└── README.md
```

## 3. Настройка .env

```env
# Bot
BOT_TOKEN=your_bot_token_here
BOT_MODE=polling

# Database
DB_ENGINE=sqlite
DB_NAME=bot.db

# Web (optional)
WEB_ENABLED=false
WEB_HOST=0.0.0.0
WEB_PORT=8080
```

## 4. Инициализация БД

```bash
tgframework init-db
```

## 5. Запуск

```bash
python main.py
```

## Первый бот (простой)

`main.py`:

```python
from tgframework import Bot, load_config

config = load_config()
bot = Bot(token=config.bot.token)

@bot.register_command("start")
async def start(update, context):
    await bot.send_message(
        context["chat"]["id"],
        f"Привет, {context['user'].get('first_name')}!"
    )

bot.run()
```

## Бот с DDD и БД

`main.py`:

```python
import asyncio
from tgframework import (
    TelegramBot,
    WebServer,
    load_config,
    create_engine,
    Session,
    UserService,
    UserRepository,
    CreateUserDTO
)

async def main():
    # 1. Конфигурация
    config = load_config()
    
    # 2. База данных
    engine = create_engine(config.database.connection_string)
    engine.connect()
    session = Session(engine)
    
    # 3. DDD сервисы
    user_service = UserService(UserRepository(session))
    
    # 4. Бот
    bot = TelegramBot(config.bot.token, session)
    
    # 5. Обработчики
    @bot.register_command("start")
    async def start(update, context):
        user_data = context["user"]
        
        # Создаем DTO
        dto = CreateUserDTO(
            user_id=user_data["id"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name")
        )
        
        # Используем сервис
        user = user_service.create_user(dto)
        
        await bot.send_message(
            context["chat"]["id"],
            f"Привет, {user.first_name}!\nВсего пользователей: {user_service.get_user_count()}"
        )
    
    # 6. Веб-сервер (optional)
    if config.web.enabled:
        web_server = WebServer(config, session, bot)
        await web_server.start()
    
    # 7. Запуск
    await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
```

## Миграции

```bash
# Создать миграцию
tgframework make:migration create_products_table

# Применить
tgframework migrate

# Откатить
tgframework migrate:rollback
```

## Веб-сервер и API

`main.py` (добавить):

```python
from tgframework.web import Router, Controller

# Контроллер
class ApiController(Controller):
    async def stats(self, request):
        return self.success({
            "users": user_service.get_user_count(),
            "status": "ok"
        })

# Роутинг
router = Router()
controller = ApiController()
router.get("/api/stats", controller.stats)

# Запуск веб-сервера
web_server = WebServer(config, session, bot)
web_server.add_router(router)
await web_server.start()
```

**Endpoints:**
- http://localhost:8080/api/stats
- http://localhost:8080/api/users
- http://localhost:8080/admin (с Telegram auth)

## Mini Apps

`.env`:

```env
MINIAPP_ENABLED=true
MINIAPP_URL=https://yourapp.com/miniapp
```

`main.py`:

```python
from tgframework.miniapp import MiniAppValidator, ReactRenderer

validator = MiniAppValidator(config.bot.token)
renderer = ReactRenderer()

# Валидация
@router.post("/miniapp/validate")
async def validate(request):
    init_data = await request.text()
    validated = validator.validate_init_data(init_data)
    return {"valid": validated}

# Рендеринг React
@router.get("/miniapp")
async def miniapp(request):
    html = renderer.render("app.html", {
        "user": {"name": "John"},
        "api_url": "http://localhost:8080/api"
    })
    return web.Response(text=html, content_type="text/html")
```

## Примеры

### 1. Inline клавиатура

```python
from tgframework import InlineKeyboardBuilder

@bot.register_command("menu")
async def menu(update, context):
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Профиль", callback_data="profile")
    keyboard.add_button("Настройки", callback_data="settings")
    keyboard.row()
    keyboard.add_button("Помощь", callback_data="help")
    
    await bot.send_message(
        context["chat"]["id"],
        "Выберите действие:",
        reply_markup=keyboard.build()
    )
```

### 2. Callback обработчик

```python
@bot.register_callback_handler(lambda data: data.startswith("profile"))
async def profile_callback(update, context):
    user = user_service.get_user(context["user"]["id"])
    
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        f"Профиль: {user.username}"
    )
```

### 3. FSM (State Machine)

```python
from tgframework.features import StatesGroup, FSMState

class RegistrationStates(StatesGroup):
    NAME = FSMState("name")
    AGE = FSMState("age")

@bot.register_command("register")
async def register_start(update, context):
    bot.state_machine.set_state(context["user"]["id"], RegistrationStates.NAME)
    await bot.send_message(context["chat"]["id"], "Введите имя:")

@bot.register_message_handler()
async def process_name(update, context):
    state = bot.state_machine.get_state(context["user"]["id"])
    
    if state == RegistrationStates.NAME:
        bot.state_machine.set_state(context["user"]["id"], RegistrationStates.AGE)
        await bot.send_message(context["chat"]["id"], "Введите возраст:")
```

### 4. Quiz

```python
from tgframework.features import Quiz, QuizQuestion

@bot.register_command("quiz")
async def quiz_start(update, context):
    quiz = Quiz(session, context["user"]["id"])
    
    quiz.add_question(QuizQuestion(
        question="Столица России?",
        options=["Москва", "Питер", "Казань"],
        correct_answer=0,
        explanation="Правильно! Москва - столица России"
    ))
    
    await quiz.start(bot, context["chat"]["id"])
```

### 5. Middleware

```python
from tgframework.application import Middleware

class LoggingMiddleware(Middleware):
    async def process(self, update, context, next_handler):
        print(f"User {context['user']['id']} sent: {update.get('text')}")
        return await next_handler(update, context)

bot.add_middleware(LoggingMiddleware())
```

### 6. PostgreSQL

`.env`:

```env
DB_ENGINE=postgresql
DB_NAME=mybot
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=secret
```

Всё остальное работает так же!

## Следующие шаги

1. Читайте [ARCHITECTURE.md](ARCHITECTURE.md) для понимания DDD
2. Смотрите [DDD_EXAMPLES.md](DDD_EXAMPLES.md) для примеров
3. Изучайте [examples/](examples/) в репозитории
4. Читайте полную документацию в [README.md](README.md)

## Помощь

- GitHub: https://github.com/LankiSer/TgBotFramework
- Issues: https://github.com/LankiSer/TgBotFramework/issues

Успехов в разработке!

