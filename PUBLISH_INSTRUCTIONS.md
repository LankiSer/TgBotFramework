# Инструкция по публикации новой версии на PyPI

## Быстрый способ (рекомендуется)

### 1. Обновите версию

Откройте `tgframework/__init__.py` и измените версию (если нужно):

```python
__version__ = "2.0.1"  # Новая версия
```

### 2. Используйте скрипт публикации

```bash
python publish.py
```

Скрипт автоматически:
- Очистит старые сборки
- Соберет новый пакет
- Проверит пакет
- Попросит подтверждение
- Загрузит на PyPI

При запросе введите:
- Username: `__token__`
- Password: ваш токен API (начинается с `pypi-`)

## Ручной способ

### 1. Обновите версию

```python
# tgframework/__init__.py
__version__ = "2.0.1"  # Новая версия
```

### 2. Очистите старые сборки

```bash
# Windows
rmdir /s /q build dist *.egg-info 2>nul

# Linux/Mac
rm -rf build dist *.egg-info
```

### 3. Соберите пакет

```bash
python -m build
```

### 4. Проверьте пакет

```bash
python -m twine check dist/*
```

### 5. Загрузите на PyPI

```bash
python -m twine upload dist/*
```

При запросе:
- Username: `__token__`
- Password: ваш токен API (начинается с `pypi-`)

## Тестовая публикация (рекомендуется сначала)

Перед публикацией на основной PyPI, протестируйте на Test PyPI:

```bash
python publish.py test
```

Или вручную:

```bash
python -m twine upload --repository testpypi dist/*
```

## Проверка после публикации

1. Проверьте страницу пакета: https://pypi.org/project/tgframework-bot/
2. Проверьте установку:

```bash
pip install --upgrade tgframework-bot
python -c "import tgframework; print(tgframework.__version__)"
```

## Важно

- Версия в `tgframework/__init__.py` должна быть уникальной (не может повторяться)
- Если версия уже существует на PyPI, получите ошибку "File already exists"
- Используйте семантическое версионирование: MAJOR.MINOR.PATCH (например, 2.0.1, 2.1.0, 3.0.0)

## Семантическое версионирование

- **PATCH** (2.0.0 → 2.0.1): Исправления багов, не ломающие обратную совместимость
- **MINOR** (2.0.0 → 2.1.0): Новые функции, не ломающие обратную совместимость
- **MAJOR** (2.0.0 → 3.0.0): Критические изменения, ломающие обратную совместимость

## Решение проблем

### Ошибка: "File already exists"
Версия уже существует на PyPI. Обновите версию в `tgframework/__init__.py`.

### Ошибка: "Invalid API token"
Проверьте, что используете правильный токен (начинается с `pypi-`) и вводите его как пароль при username `__token__`.

### Ошибка при сборке
Убедитесь, что установлены инструменты:

```bash
pip install --upgrade build twine
```

