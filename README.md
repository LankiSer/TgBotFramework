# TgFramework

Полнофункциональный фреймворк для разработки Telegram ботов

## Версия 3.0 доступна!

Новая мажорная версия с DDD архитектурой, собственной ORM, веб-сервером и поддержкой Mini Apps.

### Новые возможности

- **DDD/DTO архитектура** - правильное разделение на слои
- **Собственная ORM** - работа с SQLite и PostgreSQL
- **CLI генератор** - создание проектов одной командой
- **Веб-сервер с админ-панелью** - готовая админка с Telegram авторизацией
- **React/Next.js интеграция** - серверный рендеринг
- **Mini Apps** - полная поддержка Telegram Mini Apps
- **Конфигурация через .env** - все настройки в одном месте

### Полная обратная совместимость

Весь код версии 2.x продолжает работать в 3.0 без изменений!

## Быстрый старт

### Установка

```bash
pip install tgframework-bot
```

### Создание проекта

```bash
tgframework create-project my_bot
cd my_bot
pip install -r requirements.txt
# Настроить .env (добавить BOT_TOKEN)
python main.py
```

### Простой бот

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

## Документация

- [Быстрый старт](QUICKSTART.md) - начните за 1 минуту
- [Полная документация v3.0](README_V3.md) - все возможности
- [Руководство по миграции](MIGRATION_GUIDE.md) - переход с 2.x
- [Changelog](CHANGELOG_V3.md) - что нового

## Роутинг в стиле Laravel

TgFramework 3.0 включает мощную систему роутинга для веб-части:

```python
from tgframework.web import Router, Controller

router = Router()

# Декораторы для маршрутов
@router.get("/api/users")
async def get_users(request):
    return {"users": [...]}

@router.post("/api/users")
async def create_user(request):
    data = await request.json()
    return {"success": True, "user": data}

# Группировка маршрутов
with router.group(prefix="/api"):
    router.get("/stats", stats_controller.index)
    router.post("/send", send_controller.store)

# RESTful ресурсы
router.resource("/products", product_controller)
```

### Контроллеры

Создавайте контроллеры для организации кода:

```python
from tgframework.web import Controller

class ApiController(Controller):
    async def index(self, request):
        return self.success({"message": "API v3.0"})
    
    async def users(self, request):
        # Логика получения пользователей
        return self.success(users_list)
    
    async def error_example(self, request):
        return self.error("Not found", status=404)
```

Встроенные endpoints:
- `/api/users` - список пользователей
- `/api/users/{id}` - детали пользователя
- `/api/stats` - статистика бота
- `/miniapp` - Mini App интерфейс
- `/admin` - админ-панель

## Основные возможности

### База данных
- Встроенная ORM с поддержкой SQLite и PostgreSQL
- Автоматические миграции
- Domain модели и DTO
- Repository и Service паттерны

### Bot API
- Polling и Webhook режимы
- FSM (Finite State Machine)
- Фильтры и middleware
- Pagination
- Rate limiting
- Система квизов

### Веб-сервер
- Встроенный веб-сервер на aiohttp
- Админ-панель с Telegram авторизацией
- REST API
- CORS поддержка

### Mini Apps
- Валидация данных от Mini App
- React/Next.js интеграция
- Серверный рендеринг с переменными

### CLI
- Генератор проектов с правильной DDD структурой
- Управление миграциями
- Инициализация базы данных

## Примеры

### Бот с базой данных (новый API)

```python
import asyncio
from tgframework import TelegramBot, load_config, create_engine, Session
from tgframework.domain import UserService, UserRepository

async def main():
    config = load_config()
    engine = create_engine(config.database.connection_string)
    engine.connect()
    
    session = Session(engine)
    bot = TelegramBot(config.bot.token, session)
    
    user_service = UserService(UserRepository(session))
    
@bot.register_command("start")
    async def start(update, context):
        user = context["user"]
        # Автоматическое сохранение через сервис
        # ...
        await bot.send_message(
            context["chat"]["id"],
            f"Всего пользователей: {user_service.get_user_count()}"
        )
    
await bot.start_polling()

asyncio.run(main())
```

### Бот с веб-сервером и админкой

```python
from tgframework.web import WebServer

# ... setup ...

if config.web.enabled:
    web_server = WebServer(config, session, bot)
    await web_server.start()
    # Админ-панель на http://localhost:8080/admin
```

### Переключение БД через .env

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

## Структура проекта (DDD)

```
my_bot/
├── app/                    # Application слой
│   ├── handlers/          # Обработчики
│   ├── middlewares/       # Middleware
│   └── keyboards/         # Клавиатуры
├── domain/                # Domain слой
│   ├── models/           # Domain модели
│   ├── services/         # Бизнес-логика
│   ├── repositories/     # Репозитории
│   └── dto/              # DTO
├── infrastructure/        # Infrastructure слой
│   └── database/         # БД настройки
├── web/                  # Веб-приложение
│   ├── templates/        # Шаблоны
│   └── static/           # Статика
├── .env                  # Конфигурация
└── main.py              # Entry point
```

## CLI команды

```bash
# Создать проект
tgframework create-project my_bot

# Инициализировать БД
tgframework init-db

# Запустить миграции
tgframework migrate
```

## Сравнение с другими фреймворками

| Функция | TgFramework 3.0 | aiogram | python-telegram-bot |
|---------|-----------------|---------|---------------------|
| DDD архитектура | ✓ | ✗ | ✗ |
| Собственная ORM | ✓ | ✗ | ✗ |
| SQLite/PostgreSQL | ✓ | ✗ | ✗ |
| CLI генератор | ✓ | ✗ | ✗ |
| Админ-панель | ✓ | ✗ | ✗ |
| Mini Apps | ✓ | Частично | ✗ |
| React интеграция | ✓ | ✗ | ✗ |

## Требования

- Python 3.8+
- aiohttp
- python-dotenv
- psycopg2-binary (для PostgreSQL)

## Установка

```bash
# Базовая установка
pip install tgframework-bot

# С PostgreSQL
pip install tgframework-bot[postgresql]

# Полная установка
pip install tgframework-bot[all]
```

## Примеры в репозитории

В папке `examples/` находятся примеры ботов:

- `simple_bot.py` - простой бот с базовыми командами
- `quiz_bot.py` - бот с системой квизов
- `admin_bot.py` - бот с регистрацией и админкой
- `advanced_bot.py` - продвинутый бот с FSM и фильтрами

## Миграция с 2.x

Версия 3.0 полностью обратно совместима. Ваш существующий код продолжит работать без изменений.

Для использования новых возможностей см. [Руководство по миграции](MIGRATION_GUIDE.md).

## Лицензия

MIT License

## Поддержка

- GitHub Issues: https://github.com/LankiSer/TgBotFramework/issues
- Email: kostricyn50@mail.ru

## Авторы

TgFramework Team

---

**Начните использовать TgFramework 3.0 прямо сейчас!**

```bash
tgframework create-project my_awesome_bot
```
