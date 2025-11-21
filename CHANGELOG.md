# Changelog

## [3.0.0] - 2025-11-21

### Полное переписывание фреймворка

#### Новая архитектура DDD/DTO

**Core:**
- Система конфигурации через .env
- Специализированные исключения

**ORM:**
- Поддержка SQLite и PostgreSQL
- Query Builder
- Система миграций в стиле Laravel
- Session management для транзакций

**Domain (DDD):**
- Domain модели (User, Chat, Message, UserState)
- Data Transfer Objects (DTO)
- Repository паттерн
- Service паттерн для бизнес-логики

**Application:**
- Handlers (commands, callbacks, messages)
- Keyboards (Inline, Reply)
- Filters для обработчиков
- Middleware система
- State Machine
- Pagination

**Infrastructure:**
- Rate Limiter для Telegram API
- Utility функции

**Features:**
- Quiz система
- FSM (Finite State Machine)

**Web:**
- Роутинг в стиле Laravel
- MVC контроллеры
- API endpoints
- Admin панель с Telegram авторизацией
- CORS support

**Mini Apps:**
- Валидация данных
- React/Next.js рендеринг
- Server-side props

**CLI:**
- `create-project` - генератор проектов
- `init-db` - инициализация БД
- `migrate` - применить миграции
- `migrate:rollback` - откатить миграции
- `migrate:reset` - сбросить все миграции
- `migrate:refresh` - пересоздать БД
- `migrate:fresh` - полная очистка
- `migrate:status` - статус миграций
- `make:migration` - создать миграцию

### Breaking Changes

- Полностью изменена структура проекта
- Database класс теперь Session (через ORM)
- Все старые файлы реорганизованы по слоям
- Удалены эмодзи из кода

### Migration Guide

**Было:**
```python
from tgframework import Bot, Database

db = Database("bot.db")
bot = Bot(token)
```

**Стало:**
```python
from tgframework import TelegramBot, load_config, create_engine, Session

config = load_config()
engine = create_engine(config.database.connection_string)
session = Session(engine)
bot = TelegramBot(config.bot.token, session)
```

**Миграции:**

Было: Хардкод таблиц в database.py
```python
cursor.execute("CREATE TABLE IF NOT EXISTS users (...)")
```

Стало: Laravel-like миграции
```bash
tgframework make:migration create_users_table
tgframework migrate
```

### Улучшения

- Четкое разделение на слои (DDD)
- DTO для передачи данных
- Repository для работы с БД
- Service для бизнес-логики
- Laravel-like роутинг
- Laravel-like миграции
- Поддержка PostgreSQL
- Telegram Mini Apps support
- React/Next.js integration
- Админ-панель с Telegram auth

### Удалено

- Хардкод инициализации БД
- Все эмодзи из кода
- Старые MD файлы (README_V3.md и т.д.)
- Старые файлы bot.py, database.py из корня

## [2.x.x] - Предыдущие версии

См. старые релизы на GitHub.

