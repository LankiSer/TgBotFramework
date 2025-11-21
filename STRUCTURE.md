# Структура TgFramework 3.0

## Архитектура

```
tgframework/
├── core/                      # Ядро фреймворка
│   ├── config.py             # Система конфигурации (.env)
│   └── exceptions.py         # Специализированные исключения
│
├── orm/                       # Собственная ORM
│   ├── engine.py             # DatabaseEngine (SQLite/PostgreSQL)
│   ├── models.py             # Model, Field классы
│   ├── query.py              # QueryBuilder
│   ├── session.py            # Session для транзакций
│   └── migrations.py         # Система миграций
│
├── domain/                    # Domain слой (DDD)
│   ├── models.py             # Domain модели (User, Chat, Message)
│   ├── dto.py                # Data Transfer Objects
│   ├── repositories.py       # Repository паттерн
│   └── services.py           # Бизнес-логика
│
├── bot/                       # Telegram Bot
│   └── telegram_bot.py       # Основной класс бота
│
├── cli/                       # CLI команды
│   └── commands.py           # Генератор проектов, миграции
│
├── web/                       # Веб-сервер
│   ├── server.py             # WebServer на aiohttp
│   ├── routing.py            # Роутинг в стиле Laravel
│   ├── auth.py               # Telegram авторизация
│   └── controllers/          # Контроллеры
│       ├── api_controller.py     # API endpoints
│       ├── miniapp_controller.py # Mini App
│       └── admin_controller.py   # Админ-панель
│
├── miniapp/                   # Telegram Mini Apps
│   ├── validator.py          # Валидация данных Mini App
│   └── renderer.py           # React/Next.js рендеринг
│
└── [legacy modules]           # Старые модули (совместимость)
    ├── bot.py
    ├── database.py
    ├── handlers.py
    ├── keyboards.py
    ├── state.py
    ├── fsm.py
    ├── filters.py
    ├── pagination.py
    ├── rate_limiter.py
    ├── middleware.py
    ├── quiz.py
    └── utils.py
```

## Генерируемая структура проекта

При создании проекта через CLI:

```bash
tgframework create-project my_bot
```

Создается:

```
my_bot/
├── app/                       # Application слой
│   ├── handlers/
│   │   ├── commands/         # Команды бота
│   │   │   ├── start.py
│   │   │   ├── help.py
│   │   │   └── admin.py
│   │   ├── callbacks/        # Callback обработчики
│   │   │   └── button_handler.py
│   │   └── messages/         # Обработчики сообщений
│   │       └── echo.py
│   ├── middlewares/          # Middleware
│   ├── keyboards/            # Клавиатуры
│   └── filters/              # Фильтры
│
├── domain/                    # Domain слой
│   ├── models/               # Domain модели
│   ├── services/             # Бизнес-логика
│   ├── repositories/         # Репозитории
│   └── dto/                  # DTO
│
├── infrastructure/            # Infrastructure слой
│   └── database/
│       └── setup.py          # Настройка БД
│
├── web/                       # Веб-приложение
│   ├── routes.py             # Определение маршрутов
│   ├── controllers/          # Контроллеры
│   │   ├── api_controller.py
│   │   └── web_controller.py
│   ├── templates/            # HTML шаблоны
│   └── static/               # Статические файлы
│       ├── css/
│       └── js/
│
├── config/                    # Конфигурация
├── .env                       # Переменные окружения
├── .env.example              # Пример конфигурации
├── .gitignore                # Git ignore
├── main.py                   # Entry point
├── requirements.txt          # Зависимости
└── README.md                 # Документация
```

## Слои и их ответственность

### Core
- Конфигурация через .env
- Базовые исключения
- Утилиты

### ORM
- Работа с базой данных
- Абстракция над SQLite и PostgreSQL
- Query Builder
- Миграции

### Domain (DDD)
- **Models**: Бизнес-сущности
- **DTO**: Передача данных между слоями
- **Repositories**: Работа с БД
- **Services**: Бизнес-логика

### Application
- **Handlers**: Обработчики событий бота
- **Middlewares**: Промежуточная обработка
- **Keyboards**: UI элементы
- **Filters**: Фильтрация событий

### Infrastructure
- Настройка БД
- Внешние сервисы
- Конфигурация окружения

### Web
- **Server**: Веб-сервер на aiohttp
- **Routing**: Роутинг в стиле Laravel
- **Controllers**: MVC контроллеры
- **Auth**: Авторизация

### Mini Apps
- Валидация данных от Telegram
- Рендеринг React/Next.js
- Интеграция с Web App API

## Потоки данных

### Bot → Domain → Database
```
Telegram Update
    → Bot Handler
        → Domain Service
            → Repository
                → ORM
                    → Database
```

### Web Request → Controller → Domain → Response
```
HTTP Request
    → Router
        → Controller
            → Domain Service
                → Repository
                    → ORM
                        → Database
            ← Response
        ← HTTP Response
```

### Mini App → Validation → API → Domain
```
Mini App Data
    → MiniAppValidator
        → API Controller
            → Domain Service
                → Repository
                    → Database
```

## Конфигурация

Вся конфигурация через `.env`:

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

## Расширение

### Создание своего контроллера

```python
from tgframework.web import Controller

class MyController(Controller):
    async def index(self, request):
        return self.success({"message": "Hello"})
```

### Создание своего сервиса

```python
from domain.repositories import UserRepository

class MyService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def do_something(self, user_id: int):
        user = self.user_repo.get_by_id(user_id)
        # Бизнес-логика
```

### Добавление маршрутов

```python
from tgframework.web import Router

router = Router()

with router.group(prefix="/api/v1"):
    router.get("/endpoint", my_controller.handler)
```

## Преимущества архитектуры

1. **Разделение ответственности** - каждый слой имеет свою задачу
2. **Тестируемость** - легко тестировать отдельные компоненты
3. **Масштабируемость** - легко добавлять новые функции
4. **Поддерживаемость** - понятная структура кода
5. **Переиспользование** - компоненты можно использовать повторно

## Миграция с 2.x

Старая структура (flat):
```
my_bot/
├── bot.py
├── handlers.py
└── database.py
```

Новая структура (DDD):
```
my_bot/
├── app/handlers/
├── domain/services/
├── infrastructure/database/
└── web/controllers/
```

Обратная совместимость сохранена - старый код работает без изменений!

