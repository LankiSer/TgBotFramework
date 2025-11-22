# Обновление TgFramework до версии 3.1.2

## Проблема

Если вы видите ошибку:
```
ModuleNotFoundError: No module named 'tgframework.web.admin'
```

Это означает, что у вас установлена старая версия.

## Решение 1: Переустановка из локальных файлов (рекомендуется)

### Шаг 1: Перейдите в директорию TgBotFramework
```bash
cd C:\botLib\TgBotFramework
```

### Шаг 2: Переустановите в ваш venv
```bash
# Активируйте ваш venv
C:\tgbots\bot1\venv\Scripts\Activate.ps1

# Удалите старую версию
pip uninstall tgframework-bot -y

# Установите новую версию из исходников
pip install -e .
```

### Шаг 3: Проверьте версию
```bash
python -c "import tgframework; print(tgframework.__version__)"
# Должно быть: 3.1.2
```

### Шаг 4: Теперь создайте проект
```bash
cd C:\tgbots\bot1
tgframework create-project my_bot
```

## Решение 2: Через wheel файл

### Шаг 1: Соберите wheel
```bash
cd C:\botLib\TgBotFramework
pip install wheel setuptools
python setup.py sdist bdist_wheel
```

### Шаг 2: Установите wheel в venv
```bash
C:\tgbots\bot1\venv\Scripts\Activate.ps1
pip uninstall tgframework-bot -y
pip install dist/tgframework_bot-3.1.2-py3-none-any.whl --force-reinstall
```

### Шаг 3: Проверьте
```bash
tgframework --help
```

## Решение 3: Прямая установка в venv из исходников

```bash
# В PowerShell
cd C:\tgbots\bot1
.\venv\Scripts\Activate.ps1

# Удалите старую версию
pip uninstall tgframework-bot -y

# Установите из исходников
pip install C:\botLib\TgBotFramework -e
```

## Проверка что всё работает

```bash
python -c "from tgframework import ReactRenderer, get_telegram_user_photo_url; print('OK')"
```

Если нет ошибок - всё готово!

## Быстрая команда (всё в одном)

```powershell
cd C:\tgbots\bot1
.\venv\Scripts\Activate.ps1
pip uninstall tgframework-bot -y
pip install C:\botLib\TgBotFramework -e
python -c "import tgframework; print('Version:', tgframework.__version__)"
```

## Что нового в 3.1.2

- ✅ React + TypeScript интеграция
- ✅ ReactRenderer для SSR
- ✅ get_telegram_user_photo_url() - автоматические аватарки
- ✅ Исправлена кодировка UTF-8
- ✅ Все CLI сообщения на английском
- ✅ Удален AdminPanel (используйте AdminController)

## Проблемы?

Если ошибки продолжаются:

1. Полностью удалите venv и создайте заново:
```bash
Remove-Item -Recurse -Force C:\tgbots\bot1\venv
python -m venv C:\tgbots\bot1\venv
C:\tgbots\bot1\venv\Scripts\Activate.ps1
pip install C:\botLib\TgBotFramework -e
```

2. Проверьте, что нет конфликтов:
```bash
pip list | Select-String tgframework
```

3. Проверьте импорты:
```bash
python -c "from tgframework.web import WebServer, TelegramAuth, Router, Controller; print('Imports OK')"
```

