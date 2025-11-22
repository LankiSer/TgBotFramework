# Сборка и установка TgFramework 3.0.1

## Для разработчиков

### 1. Установка зависимостей для сборки

```bash
# В виртуальной среде где будете собирать
pip install setuptools wheel twine
```

### 2. Сборка пакета

```bash
cd C:\botLib\TgBotFramework

# Очистка старых сборок (опционально)
rmdir /s /q dist build tgframework_bot.egg-info

# Сборка
python setup.py sdist bdist_wheel
```

Будут созданы файлы:
- `dist/tgframework_bot-3.0.1.tar.gz`
- `dist/tgframework_bot-3.0.1-py3-none-any.whl`

### 3. Локальная установка

```bash
# Установка из локального файла
pip install dist/tgframework_bot-3.0.1-py3-none-any.whl

# Или в режиме разработки
pip install -e .
```

### 4. Публикация на PyPI

```bash
# Загрузка на Test PyPI (для тестирования)
twine upload --repository testpypi dist/*

# Загрузка на PyPI (production)
twine upload dist/*
```

## Для пользователей

### Установка из PyPI

```bash
# Базовая установка (SQLite)
pip install tgframework-bot

# С PostgreSQL
pip install tgframework-bot[postgresql]

# Все зависимости
pip install tgframework-bot[all]
```

### Обновление

```bash
pip install --upgrade tgframework-bot
```

### Проверка версии

```bash
pip show tgframework-bot
```

Или в Python:

```python
import tgframework
print(tgframework.__version__)  # 3.0.1
```

## Быстрый тест после установки

```bash
# Проверка CLI
tgframework --help

# Создание тестового проекта
tgframework create-project test_bot
cd test_bot

# Проверка что всё работает
python -c "from tgframework import TelegramBot, load_config; print('OK')"
```

## Структура пакета

После установки будет доступно:

```
tgframework/
├── __init__.py              # Версия 3.0.1
├── core/                    # Конфигурация
├── orm/                     # ORM + миграции
├── domain/                  # DDD модели
├── application/             # Handlers, keyboards
├── infrastructure/          # Utils, rate limiter
├── features/                # Quiz, FSM
├── bot/                     # Telegram bot
├── web/                     # Веб-сервер
├── miniapp/                 # Mini Apps
└── cli/                     # CLI команды
```

## Troubleshooting

### Ошибка: ModuleNotFoundError: No module named 'tgframework.web.admin'

**Решение:** Обновите до версии 3.0.1

```bash
pip install --upgrade --force-reinstall tgframework-bot
```

### Ошибка: ModuleNotFoundError: No module named 'aiohttp'

**Решение:** Установите зависимости

```bash
pip install aiohttp python-dotenv
```

### Ошибка: cannot import name 'AdminPanel'

**Решение:** AdminPanel удален в версии 3.0.1. Используйте:

```python
# Вместо AdminPanel используйте AdminController
from tgframework.web.controllers import AdminController
```

### Старая версия устанавливается

**Решение:** Очистите кеш pip

```bash
pip cache purge
pip install --no-cache-dir tgframework-bot
```

## Разработка

### Установка в режиме разработки

```bash
cd C:\botLib\TgBotFramework
pip install -e .
```

Изменения в коде будут сразу доступны без переустановки.

### Запуск тестов

```bash
pytest tests/
```

### Проверка кода

```bash
# Форматирование
black tgframework/

# Линтер
flake8 tgframework/

# Типы
mypy tgframework/
```

## Публикация (для мантейнеров)

### 1. Обновите версию

В `tgframework/__init__.py`:
```python
__version__ = "3.0.1"
```

### 2. Обновите CHANGELOG.md

Добавьте описание изменений для новой версии.

### 3. Соберите пакет

```bash
python setup.py sdist bdist_wheel
```

### 4. Проверьте пакет

```bash
twine check dist/*
```

### 5. Загрузите на Test PyPI

```bash
twine upload --repository testpypi dist/*
```

### 6. Протестируйте

```bash
pip install --index-url https://test.pypi.org/simple/ tgframework-bot
```

### 7. Загрузите на PyPI

```bash
twine upload dist/*
```

### 8. Создайте Git тег

```bash
git tag v3.0.1
git push origin v3.0.1
```

## Системные требования

- Python >= 3.8
- pip >= 20.0
- Для сборки: setuptools, wheel
- Для публикации: twine

## Зависимости

**Обязательные:**
- aiohttp >= 3.9.0
- python-dotenv >= 1.0.0

**Опциональные:**
- psycopg2-binary >= 2.9.0 (для PostgreSQL)

## Заключение

TgFramework 3.0.1 готов к установке и использованию!

Для вопросов: https://github.com/LankiSer/TgBotFramework/issues

