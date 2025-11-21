# Архитектура TgFramework 3.0

## Общий обзор

TgFramework 3.0 полностью построен на принципах **DDD (Domain-Driven Design)** и **DTO (Data Transfer Objects)** с четким разделением на слои.

## Структура

```
tgframework/
├── core/               # Ядро фреймворка
├── orm/                # ORM слой
├── domain/             # Domain слой (DDD)
├── application/        # Application слой
├── infrastructure/     # Infrastructure слой
├── features/           # Features слой
├── bot/                # Bot слой
├── web/                # Web слой
├── miniapp/            # Mini Apps слой
└── cli/                # CLI слой
```

## Слои архитектуры

### 1. Core (Ядро)

**Ответственность:** Базовая конфигурация и исключения

**Содержит:**
- `config.py` - Система конфигурации через .env
- `exceptions.py` - Специализированные исключения

**Пример:**
```python
from tgframework.core import load_config, ConfigException

config = load_config()  # Загрузка из .env
```

### 2. ORM (Object-Relational Mapping)

**Ответственность:** Работа с базой данных

**Содержит:**
- `engine.py` - DatabaseEngine (SQLite/PostgreSQL)
- `models.py` - Model, Field классы
- `query.py` - QueryBuilder
- `session.py` - Session для транзакций
- `migrations.py` - Система миграций

**Пример:**
```python
from tgframework.orm import create_engine, Session, Migration

engine = create_engine(config.database.connection_string)
session = Session(engine)
```

### 3. Domain (DDD)

**Ответственность:** Бизнес-логика и модели предметной области

**Содержит:**
- `models.py` - Domain модели (User, Chat, Message)
- `dto.py` - Data Transfer Objects
- `repositories.py` - Repository паттерн
- `services.py` - Бизнес-логика

**Принципы:**
- Модели содержат бизнес-логику
- DTO для передачи данных между слоями
- Repositories инкапсулируют доступ к данным
- Services содержат бизнес-операции

**Пример:**
```python
from tgframework.domain import (
    User,                    # Domain модель
    UserDTO,                 # DTO для передачи
    UserRepository,          # Репозиторий
    UserService              # Сервис с бизнес-логикой
)

# Сервис использует репозиторий
user_service = UserService(UserRepository(session))
user = user_service.get_user(123)  # Возвращает DTO
```

### 4. Application

**Ответственность:** Обработка событий и UI

**Содержит:**
- `handlers.py` - CommandHandler, CallbackHandler, MessageHandler
- `keyboards.py` - InlineKeyboardBuilder, ReplyKeyboardBuilder
- `filters.py` - Фильтры для обработчиков
- `middleware.py` - Middleware система
- `state_machine.py` - Управление состояниями
- `pagination.py` - Пагинация

**Пример:**
```python
from tgframework.application import (
    CommandHandler,
    InlineKeyboardBuilder,
    Filters,
    StateMachine
)

keyboard = InlineKeyboardBuilder()
keyboard.add_button("Кнопка", callback_data="data")
```

### 5. Infrastructure

**Ответственность:** Внешние сервисы и утилиты

**Содержит:**
- `rate_limiter.py` - Rate limiting для Telegram API
- `utils.py` - Вспомогательные функции

**Пример:**
```python
from tgframework.infrastructure import (
    TelegramRateLimiter,
    parse_command,
    format_text
)

rate_limiter = TelegramRateLimiter()
await rate_limiter.wait_message(user_id)
```

### 6. Features

**Ответственность:** Дополнительные функции

**Содержит:**
- `quiz.py` - Система квизов
- `fsm.py` - FSM (Finite State Machine)

**Пример:**
```python
from tgframework.features import Quiz, FSMState

quiz = Quiz(db, user_id)
quiz.add_question(question)
```

### 7. Bot

**Ответственность:** Telegram бот

**Содержит:**
- `telegram_bot.py` - Основной класс бота

**Пример:**
```python
from tgframework.bot import TelegramBot

bot = TelegramBot(token, session)
```

### 8. Web

**Ответственность:** Веб-сервер, API, админка

**Содержит:**
- `server.py` - WebServer на aiohttp
- `routing.py` - Роутинг в стиле Laravel
- `auth.py` - Telegram авторизация
- `controllers/` - MVC контроллеры

**Пример:**
```python
from tgframework.web import Router, Controller

router = Router()

@router.get("/api/users")
async def get_users(request):
    return {"users": [...]}
```

### 9. Mini Apps

**Ответственность:** Поддержка Telegram Mini Apps

**Содержит:**
- `validator.py` - Валидация данных от Mini App
- `renderer.py` - React/Next.js рендеринг

**Пример:**
```python
from tgframework.miniapp import MiniAppValidator, ReactRenderer

validator = MiniAppValidator(bot_token)
validated = validator.validate_init_data(init_data)
```

### 10. CLI

**Ответственность:** Инструменты командной строки

**Содержит:**
- `commands.py` - CLI команды
- `migration_templates.py` - Шаблоны миграций

**Пример:**
```bash
tgframework create-project my_bot
tgframework migrate
tgframework make:migration create_table
```

## Потоки данных

### Bot → Domain → Database

```
Telegram Update
    ↓
Bot Handler (application)
    ↓
Domain Service (domain)
    ↓
Repository (domain)
    ↓
ORM Session (orm)
    ↓
Database Engine (orm)
    ↓
SQLite/PostgreSQL
```

### Web Request → Controller → Domain

```
HTTP Request
    ↓
Router (web)
    ↓
Controller (web)
    ↓
Domain Service (domain)
    ↓
Repository (domain)
    ↓
ORM (orm)
    ↓
Response
```

## Принципы

### 1. Separation of Concerns

Каждый слой имеет свою ответственность:
- **Core** - конфигурация
- **ORM** - БД
- **Domain** - бизнес-логика
- **Application** - обработка событий
- **Infrastructure** - внешние сервисы
- **Features** - дополнительные функции

### 2. Dependency Injection

Зависимости передаются через конструкторы:

```python
# Репозиторий зависит от Session
user_repo = UserRepository(session)

# Сервис зависит от Repository
user_service = UserService(user_repo)

# Контроллер зависит от Service
controller = ApiController(user_service)
```

### 3. DTO Pattern

Данные передаются через DTO:

```python
# Создание пользователя
user_dto = CreateUserDTO(
    user_id=123,
    username="john",
    first_name="John"
)

# Сервис принимает DTO
user = user_service.create_user(user_dto)

# Возвращает DTO
result: UserDTO = user_service.get_user(123)
```

### 4. Repository Pattern

Доступ к данным через репозитории:

```python
class UserRepository:
    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.session.get(User, user_id)
    
    def create(self, user_dto: CreateUserDTO) -> User:
        user = User(**user_dto.__dict__)
        return self.session.add(user)
```

### 5. Service Pattern

Бизнес-логика в сервисах:

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.repo = user_repo
    
    def get_user(self, user_id: int) -> Optional[UserDTO]:
        user = self.repo.get_by_id(user_id)
        return self._to_dto(user) if user else None
```

## Преимущества архитектуры

### 1. Тестируемость

Каждый слой можно тестировать независимо:

```python
# Mock репозиторий
mock_repo = Mock(UserRepository)
service = UserService(mock_repo)

# Тестируем сервис без БД
result = service.get_user(123)
```

### 2. Масштабируемость

Легко добавлять новые функции:

```python
# Новый сервис
class OrderService:
    def __init__(self, order_repo, user_repo):
        self.order_repo = order_repo
        self.user_repo = user_repo
    
    def create_order(self, user_id, product_id):
        # Бизнес-логика
        pass
```

### 3. Поддерживаемость

Понятная структура кода:

```
domain/
  models/           # Что у нас есть
  services/         # Что мы можем делать
  repositories/     # Как мы работаем с данными
  dto/              # Как мы передаем данные
```

### 4. Гибкость

Легко менять реализацию:

```python
# Заменить SQLite на PostgreSQL
DB_ENGINE=postgresql

# Заменить репозиторий
class CachedUserRepository(UserRepository):
    def get_by_id(self, user_id):
        # Добавляем кеширование
        pass
```

## Сравнение с другими подходами

### Flat структура (старый подход)

```
my_bot/
├── bot.py          # Всё в одном файле
├── handlers.py     # Хаотичные обработчики
└── database.py     # Прямые SQL запросы
```

❌ Проблемы:
- Сложно тестировать
- Нельзя масштабировать
- Хардкод везде
- Нет разделения ответственности

### DDD структура (TgFramework 3.0)

```
my_bot/
├── domain/         # Бизнес-логика
├── application/    # Обработчики
├── infrastructure/ # Внешние сервисы
└── web/            # API
```

✅ Преимущества:
- Легко тестировать
- Масштабируется
- Чистый код
- Разделение ответственности

## Заключение

TgFramework 3.0 использует профессиональную архитектуру:
- **DDD** для организации бизнес-логики
- **DTO** для передачи данных
- **Repository** для доступа к БД
- **Service** для бизнес-операций
- **MVC** для веб-части

Это делает фреймворк мощным инструментом для создания как простых, так и сложных Telegram ботов!

