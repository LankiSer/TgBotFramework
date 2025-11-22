# Обновление до версии 3.0.1

## Что изменилось

### 1. Полная реорганизация по DDD/DTO

**Новая структура:**

```
tgframework/
├── core/               # Конфигурация, исключения
├── orm/                # ORM (SQLite/PostgreSQL)
├── domain/             # Domain модели, DTO, репозитории, сервисы
├── application/        # Handlers, keyboards, filters, middleware
├── infrastructure/     # Rate limiter, utils
├── features/           # Quiz, FSM
├── bot/                # Telegram bot
├── web/                # Веб-сервер, роутинг, контроллеры
├── miniapp/            # Mini Apps
└── cli/                # CLI команды
```

### 2. Удалены файлы

**Из корня tgframework:**
- `bot.py` → `bot/telegram_bot.py`
- `database.py` → заменен на ORM + миграции
- `handlers.py` → `application/handlers.py`
- `keyboards.py` → `application/keyboards.py`
- `filters.py` → `application/filters.py`
- `middleware.py` → `application/middleware.py`
- `state.py` → `application/state_machine.py`
- `pagination.py` → `application/pagination.py`
- `rate_limiter.py` → `infrastructure/rate_limiter.py`
- `utils.py` → `infrastructure/utils.py`
- `quiz.py` → `features/quiz.py`
- `fsm.py` → `features/fsm.py`

**MD файлы:**
- `MIGRATIONS_GUIDE.md`
- `ROUTING_EXAMPLES.md`
- `STRUCTURE.md`
- `example_migration_workflow.md`
- И другие временные MD файлы

### 3. Исправлены импорты

**Было:**
```python
from tgframework.web import AdminPanel  # ОШИБКА!
```

**Стало:**
```python
from tgframework.web import WebServer, TelegramAuth, Router, Controller
from tgframework.web.controllers import AdminController  # Если нужен админ-контроллер
```

### 4. Обновленные импорты

```python
# Core
from tgframework import load_config, Config

# ORM
from tgframework import create_engine, Session, Migration

# Domain (DDD)
from tgframework import User, UserDTO, UserService, UserRepository

# Application
from tgframework import (
    CommandHandler,
    InlineKeyboardBuilder,
    Filters,
    StateMachine
)

# Infrastructure
from tgframework import TelegramRateLimiter, parse_command

# Features
from tgframework import Quiz, FSMState

# Bot
from tgframework import TelegramBot, Bot

# Web
from tgframework import WebServer, Router, Controller
```

## Как обновиться

### Шаг 1: Обновите пакет

```bash
pip install --upgrade tgframework-bot
```

Или локально:

```bash
cd C:\botLib\TgBotFramework
pip install -e .
```

### Шаг 2: Проверьте версию

```bash
python -c "import tgframework; print(tgframework.__version__)"
# Должно быть: 3.0.1
```

### Шаг 3: Обновите импорты в вашем коде

**Старый код (не работает):**
```python
from tgframework import Bot, Database
from tgframework.web import AdminPanel  # ОШИБКА

db = Database("bot.db")
bot = Bot(token)
```

**Новый код (работает):**
```python
from tgframework import (
    TelegramBot,
    load_config,
    create_engine,
    Session
)

config = load_config()
engine = create_engine(config.database.connection_string)
session = Session(engine)
bot = TelegramBot(config.bot.token, session)
```

### Шаг 4: Создайте новый проект

```bash
tgframework create-project my_new_bot
cd my_new_bot
```

Это создаст проект с правильной DDD структурой!

## Совместимость

### ❌ Удалено

- `AdminPanel` класс (заменен на `AdminController`)
- `Database` класс (заменен на `Session` из ORM)
- Прямые импорты старых файлов из корня

### ✅ Добавлено

- Полная DDD/DTO архитектура
- Domain модели, DTO, репозитории, сервисы
- Laravel-like миграции
- Laravel-like роутинг
- Контроллеры для API, Mini Apps, Admin

### ⚠️ Изменено

- Структура проекта полностью переработана
- Все файлы разделены по слоям
- Импорты обновлены

## Примеры

### Простой бот

```python
from tgframework import Bot, load_config

config = load_config()
bot = Bot(token=config.bot.token)

@bot.register_command("start")
async def start(update, context):
    await bot.send_message(
        context["chat"]["id"],
        "Привет!"
    )

bot.run()
```

### Бот с DDD

```python
import asyncio
from tgframework import (
    TelegramBot,
    load_config,
    create_engine,
    Session,
    UserService,
    UserRepository,
    CreateUserDTO
)

async def main():
    config = load_config()
    engine = create_engine(config.database.connection_string)
    engine.connect()
    session = Session(engine)
    
    user_service = UserService(UserRepository(session))
    bot = TelegramBot(config.bot.token, session)
    
    @bot.register_command("start")
    async def start(update, context):
        user_data = context["user"]
        dto = CreateUserDTO(
            user_id=user_data["id"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name")
        )
        user = user_service.create_user(dto)
        await bot.send_message(
            context["chat"]["id"],
            f"Привет, {user.first_name}!"
        )
    
    await bot.start_polling()

asyncio.run(main())
```

### Веб-сервер

```python
from tgframework.web import Router, Controller

router = Router()

class ApiController(Controller):
    async def index(self, request):
        return self.success({"version": "3.0.1"})

controller = ApiController()
router.get("/api", controller.index)

# В main.py
from tgframework import WebServer
web_server = WebServer(config, session, bot)
web_server.add_router(router)
```

## Документация

- **ARCHITECTURE.md** - Подробная архитектура DDD/DTO
- **DDD_EXAMPLES.md** - Примеры использования DDD/DTO
- **QUICK_START.md** - Быстрый старт
- **CHANGELOG.md** - История изменений
- **README.md** - Основная документация

## Поддержка

Если у вас возникли проблемы:

1. Проверьте версию: `pip show tgframework-bot`
2. Переустановите: `pip install --upgrade --force-reinstall tgframework-bot`
3. Создайте issue: https://github.com/LankiSer/TgBotFramework/issues

## Заключение

Версия 3.0.1 - это полностью переработанный фреймворк с профессиональной архитектурой DDD/DTO, готовый к созданию как простых, так и сложных Telegram ботов!

Удачи в разработке! 🚀

