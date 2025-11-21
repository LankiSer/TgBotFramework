# TgFramework 3.0

Мощный фреймворк для разработки Telegram ботов с DDD архитектурой, собственной ORM, веб-сервером и поддержкой Mini Apps.

## Установка

```bash
pip install tgframework-bot python-dotenv

# Для PostgreSQL
pip install psycopg2-binary
```

## Быстрый старт

```bash
# 1. Создать проект
tgframework create-project my_bot

# 2. Перейти в проект
cd my_bot

# 3. Настроить .env (добавить BOT_TOKEN)

# 4. Инициализировать БД
tgframework init-db

# 5. Запустить
python main.py
```

## Архитектура DDD/DTO

```
tgframework/
├── core/           # Конфигурация (.env), исключения
├── orm/            # ORM с SQLite/PostgreSQL, миграции
├── domain/         # Domain модели, DTO, сервисы, репозитории
├── application/    # Handlers, keyboards, filters, middleware
├── infrastructure/ # Rate limiter, utils
├── features/       # Quiz, FSM
├── bot/            # Telegram bot
├── web/            # Веб-сервер, роутинг, контроллеры
├── miniapp/        # Mini Apps support
└── cli/            # Генератор проектов, миграции
```

## Роутинг в стиле Laravel

TgFramework 3.0 включает мощную систему роутинга для веб-части:

```python
from tgframework.web import Router, Controller

router = Router()

# Декораторы
@router.get("/api/users")
async def get_users(request):
    return {"users": [...]}

# Группировка
with router.group(prefix="/api"):
    router.get("/stats", controller.stats)
    router.post("/send", controller.send)

# RESTful ресурсы
router.resource("/products", product_controller)
```

### Контроллеры

```python
from tgframework.web import Controller

class ApiController(Controller):
    async def index(self, request):
        return self.success({"message": "API v3.0"})
    
    async def users(self, request):
        return self.success(users_list)
    
    async def error_example(self, request):
        return self.error("Not found", status=404)
```

**Встроенные endpoints:**
- `/api/users` - список пользователей
- `/api/users/{id}` - детали пользователя
- `/api/stats` - статистика бота
- `/miniapp` - Mini App интерфейс
- `/admin` - админ-панель

## Миграции в стиле Laravel

```bash
# Инициализация
tgframework init-db

# Применить миграции
tgframework migrate

# Откатить последний батч
tgframework migrate:rollback

# Откатить все
tgframework migrate:reset

# Пересоздать БД
tgframework migrate:fresh

# Статус
tgframework migrate:status

# Создать новую
tgframework make:migration create_products_table
```

### Пример миграции

```python
from tgframework.orm import Migration, DatabaseEngine

class CreateProductsTable(Migration):
    def up(self, engine: DatabaseEngine):
        is_postgres = "postgresql" in engine.connection_string
        
        query = """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL
            )
        """
        
        if is_postgres:
            query = query.replace("AUTOINCREMENT", "")
            query = query.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
        
        engine.execute(query)
        engine.commit()
    
    def down(self, engine: DatabaseEngine):
        engine.execute("DROP TABLE IF EXISTS products")
        engine.commit()
```

## ORM с SQLite/PostgreSQL

```python
from tgframework import load_config, create_engine, Session
from tgframework.domain import UserService, UserRepository

config = load_config()
engine = create_engine(config.database.connection_string)
session = Session(engine)

user_service = UserService(UserRepository(session))
users = user_service.get_all_users()
```

Переключение БД в `.env`:

```env
# SQLite
DB_ENGINE=sqlite
DB_NAME=bot.db

# PostgreSQL
DB_ENGINE=postgresql
DB_NAME=mybot
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=password
```

## Простой бот

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

## Бот с БД и веб-сервером

```python
import asyncio
from tgframework import TelegramBot, WebServer, load_config, create_engine, Session

async def main():
    config = load_config()
    engine = create_engine(config.database.connection_string)
    engine.connect()
    
    session = Session(engine)
    bot = TelegramBot(config.bot.token, session)
    
    # Веб-сервер с API и админ-панелью
    if config.web.enabled:
        web_server = WebServer(config, session, bot)
        await web_server.start()
    
    await bot.start_polling()

asyncio.run(main())
```

## Mini Apps

```python
from tgframework.miniapp import MiniAppValidator, ReactRenderer

validator = MiniAppValidator(bot_token)
renderer = ReactRenderer()

# Валидация
validated = validator.validate_init_data(init_data)

# Рендеринг с серверными переменными
html = renderer.render("app.html", context={
    "user": user_data,
    "api_url": "https://api.example.com"
})
```

## CLI Команды

```bash
# Создание проекта
tgframework create-project my_bot

# Миграции
tgframework init-db                    # Инициализация
tgframework migrate                    # Применить
tgframework migrate:rollback           # Откатить
tgframework migrate:refresh            # Обновить
tgframework migrate:fresh              # Пересоздать
tgframework migrate:status             # Статус
tgframework make:migration name        # Создать
```

## Конфигурация (.env)

```env
# Bot
BOT_TOKEN=your_token
BOT_MODE=polling

# Database  
DB_ENGINE=sqlite          # или postgresql
DB_NAME=bot.db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=

# Web
WEB_ENABLED=true
WEB_HOST=0.0.0.0
WEB_PORT=8080
WEB_SECRET_KEY=secret
ADMIN_ENABLED=true

# Mini App
MINIAPP_ENABLED=false
MINIAPP_URL=
```

## Возможности

### Core
- Конфигурация через .env
- Специализированные исключения

### ORM
- SQLite и PostgreSQL support
- Query Builder
- Миграции в стиле Laravel
- Session management

### Domain (DDD)
- Domain модели
- DTO для передачи данных
- Repositories для работы с БД
- Services для бизнес-логики

### Application
- Handlers (commands, callbacks, messages)
- Keyboards (Inline, Reply)
- Filters
- Middleware
- State Machine
- Pagination

### Infrastructure
- Rate Limiter
- Utils (форматирование, парсинг)

### Features
- Quiz система
- FSM (Finite State Machine)

### Web
- Роутинг в стиле Laravel
- Controllers (API, Admin, Mini App)
- Telegram авторизация
- CORS support

### Mini Apps
- Валидация данных
- React/Next.js рендеринг
- Server-side props

## Документация

- GitHub: https://github.com/LankiSer/TgBotFramework
- Issues: https://github.com/LankiSer/TgBotFramework/issues

## Лицензия

MIT License

## Авторы

TgFramework Team
