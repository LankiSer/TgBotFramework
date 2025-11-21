"""
CLI команды
"""

import os
import sys
from pathlib import Path
from typing import Optional
import argparse


def create_project(project_name: str, output_dir: Optional[str] = None):
    """
    Создать новый проект с правильной DDD/DTO структурой
    
    Args:
        project_name: Имя проекта
        output_dir: Директория для создания проекта
    """
    if output_dir is None:
        output_dir = os.getcwd()
    
    project_path = Path(output_dir) / project_name
    
    if project_path.exists():
        print(f"[ERROR] Проект {project_name} уже существует в {output_dir}")
        return
    
    print(f"Создание проекта {project_name}...")
    
    # Создаем структуру проекта
    directories = [
        "",
        "app",
        "app/handlers",
        "app/handlers/commands",
        "app/handlers/callbacks",
        "app/handlers/messages",
        "app/middlewares",
        "app/keyboards",
        "app/filters",
        "domain",
        "domain/models",
        "domain/services",
        "domain/repositories",
        "domain/dto",
        "infrastructure",
        "infrastructure/database",
        "migrations",
        "web",
        "web/templates",
        "web/static",
        "web/static/css",
        "web/static/js",
        "web/api",
        "web/admin",
        "config",
    ]
    
    for directory in directories:
        dir_path = project_path / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Создаем __init__.py
        if directory and not directory.startswith("web/static") and not directory.startswith("web/templates") and not directory == "config" and not directory == "migrations":
            init_file = dir_path / "__init__.py"
            init_file.write_text('"""\n' + f'{directory.replace("/", ".")} module\n' + '"""\n')
    
    # Создаем файлы конфигурации
    create_env_file(project_path)
    create_env_example(project_path)
    create_main_file(project_path, project_name)
    create_bot_file(project_path)
    create_handlers_files(project_path)
    create_domain_files(project_path)
    create_infrastructure_files(project_path)
    create_web_files(project_path)
    create_requirements_file(project_path)
    create_readme_file(project_path, project_name)
    create_gitignore_file(project_path)
    
    print(f"[SUCCESS] Проект {project_name} создан успешно!")
    print(f"\nСтруктура проекта:")
    print(f"   {project_path}/")
    print(f"   ├── app/                    # Handlers, keyboards, middlewares")
    print(f"   ├── domain/                 # Domain models, DTOs, services")
    print(f"   ├── infrastructure/         # Database, external services")
    print(f"   ├── web/                    # Web server, admin panel")
    print(f"   ├── config/")
    print(f"   ├── .env                    # Configuration")
    print(f"   ├── main.py                 # Entry point")
    print(f"   └── requirements.txt")
    print(f"\nСледующие шаги:")
    print(f"   1. cd {project_name}")
    print(f"   2. pip install -r requirements.txt")
    print(f"   3. Отредактируйте .env файл (добавьте BOT_TOKEN)")
    print(f"   4. python main.py")


def create_env_file(project_path: Path):
    """Создать .env файл"""
    env_content = """# Bot Configuration
BOT_TOKEN=your_bot_token_here
BOT_MODE=polling  # polling or webhook
WEBHOOK_URL=
WEBHOOK_SECRET=

# Database Configuration
DB_ENGINE=sqlite  # sqlite or postgresql
DB_NAME=bot.db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=

# Web Server Configuration
WEB_ENABLED=true
WEB_HOST=0.0.0.0
WEB_PORT=8080
WEB_SECRET_KEY=your-secret-key-change-this
ADMIN_ENABLED=true
CORS_ORIGINS=*

# Mini App Configuration
MINIAPP_ENABLED=false
MINIAPP_URL=
MINIAPP_SHORT_NAME=

# Other Settings
DEBUG=false
LOG_LEVEL=INFO
"""
    (project_path / ".env").write_text(env_content)


def create_env_example(project_path: Path):
    """Создать .env.example файл"""
    env_example = """# Bot Configuration
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
BOT_MODE=polling
WEBHOOK_URL=
WEBHOOK_SECRET=

# Database Configuration
DB_ENGINE=sqlite
DB_NAME=bot.db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=

# Web Server Configuration
WEB_ENABLED=true
WEB_HOST=0.0.0.0
WEB_PORT=8080
WEB_SECRET_KEY=your-secret-key-change-this
ADMIN_ENABLED=true
CORS_ORIGINS=*

# Mini App Configuration
MINIAPP_ENABLED=false
MINIAPP_URL=
MINIAPP_SHORT_NAME=

# Other Settings
DEBUG=false
LOG_LEVEL=INFO
"""
    (project_path / ".env.example").write_text(env_example)


def create_main_file(project_path: Path, project_name: str):
    """Создать main.py"""
    main_content = f'''"""
{project_name} - Telegram Bot
"""

import asyncio
import logging
from tgframework.core import load_config
from tgframework.orm import create_engine
from tgframework.orm import Session
from infrastructure.database import setup_database
from app.bot import create_bot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""
    # Загрузка конфигурации
    config = load_config()
    
    logger.info(f"Запуск бота...")
    logger.info(f"База данных: {{config.database.engine}}")
    logger.info(f"Веб-сервер: {{'Включен' if config.web.enabled else 'Выключен'}}")
    
    # Создание движка БД
    engine = create_engine(config.database.connection_string)
    engine.connect()
    
    # Настройка БД
    setup_database(engine)
    
    # Создание сессии
    session = Session(engine)
    
    # Создание бота
    bot = create_bot(config, session)
    
    # Запуск веб-сервера
    if config.web.enabled:
        from tgframework.web import WebServer
        web_server = WebServer(config, session, bot)
        await web_server.start()
        logger.info(f"Веб-сервер доступен на http://{{config.web.host}}:{{config.web.port}}")
    
    try:
        # Запуск бота
        if config.bot.mode == "polling":
            await bot.start_polling()
        else:
            await bot.start_webhook(
                host=config.web.host,
                port=config.web.port,
                path="/webhook",
                secret_token=config.bot.webhook_secret
            )
    except KeyboardInterrupt:
        logger.info("Остановка бота...")
    finally:
        await bot.stop()
        session.close()
        if config.web.enabled:
            await web_server.stop()


if __name__ == "__main__":
    asyncio.run(main())
'''
    (project_path / "main.py").write_text(main_content)


def create_bot_file(project_path: Path):
    """Создать app/bot.py"""
    bot_content = '''"""
Создание и настройка бота
"""

from tgframework import Bot
from tgframework.core import Config
from tgframework.orm import Session
from domain.repositories import UserRepository, ChatRepository, MessageRepository
from domain.services import UserService, ChatService, MessageService

# Импорт обработчиков
from app.handlers.commands import start, help_command, admin
from app.handlers.callbacks import button_handler
from app.handlers.messages import echo


def create_bot(config: Config, session: Session) -> Bot:
    """
    Создать и настроить бота
    
    Args:
        config: Конфигурация
        session: Сессия БД
        
    Returns:
        Настроенный бот
    """
    bot = Bot(token=config.bot.token)
    
    # Создание репозиториев
    user_repo = UserRepository(session)
    chat_repo = ChatRepository(session)
    message_repo = MessageRepository(session)
    
    # Создание сервисов
    user_service = UserService(user_repo)
    chat_service = ChatService(chat_repo)
    message_service = MessageService(message_repo)
    
    # Добавление сервисов в контекст бота
    bot.user_service = user_service
    bot.chat_service = chat_service
    bot.message_service = message_service
    
    # Регистрация обработчиков команд
    bot.register_command("start", start.handle, "Начать работу с ботом")
    bot.register_command("help", help_command.handle, "Показать помощь")
    bot.register_command("admin", admin.handle, "Админ панель")
    
    # Регистрация callback обработчиков
    bot.register_callback("btn_", button_handler.handle)
    
    # Регистрация обработчиков сообщений
    bot.register_message_handler(echo.handle)
    
    return bot
'''
    (project_path / "app" / "bot.py").write_text(bot_content)


def create_handlers_files(project_path: Path):
    """Создать файлы обработчиков"""
    # commands/start.py
    start_content = '''"""
Обработчик команды /start
"""

async def handle(update, context):
    """Обработать команду /start"""
    bot = context["bot"]
    chat_id = context["chat"]["id"]
    user = context["user"]
    
    # Сохранение пользователя через сервис
    from domain.dto import CreateUserDTO
    user_dto = CreateUserDTO(
        user_id=user["id"],
        username=user.get("username"),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        language_code=user.get("language_code"),
    )
    bot.user_service.create_user(user_dto)
    
    text = f"Привет, {user.get('first_name', 'пользователь')}!\\n\\n"
    text += "Это стартовый бот, созданный с помощью TgFramework.\\n\\n"
    text += "Доступные команды:\\n"
    text += "/help - Показать помощь\\n"
    text += "/admin - Админ панель"
    
    await bot.send_message(chat_id, text)
'''
    (project_path / "app" / "handlers" / "commands" / "start.py").write_text(start_content)
    
    # commands/help.py
    help_content = '''"""
Обработчик команды /help
"""

async def handle(update, context):
    """Обработать команду /help"""
    bot = context["bot"]
    chat_id = context["chat"]["id"]
    
    text = "**Помощь**\\n\\n"
    text += "Доступные команды:\\n"
    text += "/start - Начать работу\\n"
    text += "/help - Показать эту справку\\n"
    text += "/admin - Админ панель (только для админов)"
    
    await bot.send_message(chat_id, text, parse_mode="Markdown")
'''
    (project_path / "app" / "handlers" / "commands" / "help.py").write_text(help_content)
    
    # commands/admin.py
    admin_content = '''"""
Обработчик команды /admin
"""

from tgframework import InlineKeyboardBuilder


async def handle(update, context):
    """Обработать команду /admin"""
    bot = context["bot"]
    chat_id = context["chat"]["id"]
    user_id = context["user"]["id"]
    
    # Проверка прав администратора
    if not bot.user_service.is_admin(user_id):
        await bot.send_message(chat_id, "У вас нет прав администратора")
        return
    
    # Получение статистики
    user_count = bot.user_service.get_user_count()
    
    text = "**Админ панель**\\n\\n"
    text += f"Всего пользователей: {user_count}\\n"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Пользователи", callback_data="admin_users")
    keyboard.row()
    keyboard.add_button("Статистика", callback_data="admin_stats")
    
    await bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=keyboard.build())
'''
    (project_path / "app" / "handlers" / "commands" / "admin.py").write_text(admin_content)
    
    # callbacks/button_handler.py
    callback_content = '''"""
Обработчик callback кнопок
"""

async def handle(update, context):
    """Обработать callback"""
    bot = context["bot"]
    callback_query = context["callback_query"]
    callback_data = context["callback_data"]
    
    await bot.answer_callback_query(callback_query["id"], text="Кнопка нажата!")
'''
    (project_path / "app" / "handlers" / "callbacks" / "button_handler.py").write_text(callback_content)
    
    # messages/echo.py
    echo_content = '''"""
Обработчик текстовых сообщений
"""

async def handle(update, context):
    """Эхо обработчик"""
    bot = context["bot"]
    chat_id = context["chat"]["id"]
    text = context.get("text", "")
    
    if text:
        await bot.send_message(chat_id, f"Вы написали: {text}")
'''
    (project_path / "app" / "handlers" / "messages" / "echo.py").write_text(echo_content)


def create_domain_files(project_path: Path):
    """Создать файлы domain слоя"""
    # Уже созданы через импорт из tgframework


def create_infrastructure_files(project_path: Path):
    """Создать файлы infrastructure"""
    db_setup = '''"""
Настройка базы данных
"""

from tgframework.orm import DatabaseEngine, MigrationManager
from tgframework.domain.models import User, Chat, Message, UserState


def setup_database(engine: DatabaseEngine):
    """
    Настроить базу данных (создать таблицы)
    
    Args:
        engine: Движок БД
    """
    migration_manager = MigrationManager(engine)
    
    # Создание таблиц
    migration_manager.create_table_from_model(User)
    migration_manager.create_table_from_model(Chat)
    migration_manager.create_table_from_model(Message)
    migration_manager.create_table_from_model(UserState)
'''
    (project_path / "infrastructure" / "database" / "setup.py").write_text(db_setup)


def create_web_files(project_path: Path):
    """Создать файлы веб-части"""
    # web/routes.py
    routes_content = '''"""
Определение маршрутов приложения
"""

from tgframework.web import Router
from .controllers.api_controller import ApiController
from .controllers.web_controller import WebController

def register_routes(router: Router, session, bot):
    """
    Регистрация маршрутов
    
    Args:
        router: Router instance
        session: Database session
        bot: Bot instance
    """
    # Контроллеры
    api_controller = ApiController(session, bot)
    web_controller = WebController(session)
    
    # API routes
    with router.group(prefix="/api"):
        router.get("", api_controller.index, name="api.index")
        router.get("/users", api_controller.users, name="api.users")
        router.get("/stats", api_controller.stats, name="api.stats")
    
    # Web routes
    router.get("/", web_controller.index, name="home")
    router.get("/about", web_controller.about, name="about")
'''
    (project_path / "web" / "routes.py").write_text(routes_content)
    
    # web/controllers/api_controller.py
    api_controller_content = '''"""
API контроллер
"""

from tgframework.web import Controller


class ApiController(Controller):
    """Контроллер для API endpoints"""
    
    def __init__(self, session=None, bot=None):
        super().__init__()
        self.session = session
        self.bot = bot
    
    async def index(self, request):
        """GET /api"""
        return self.json({
            "name": "My Bot API",
            "version": "1.0.0"
        })
    
    async def users(self, request):
        """GET /api/users"""
        if not self.session:
            return self.error("Database not configured", 500)
        
        try:
            from domain.services import UserService
            from domain.repositories import UserRepository
            
            user_service = UserService(UserRepository(self.session))
            users = user_service.get_all_users(limit=50)
            
            return self.success([
                {
                    "user_id": u.user_id,
                    "username": u.username,
                    "first_name": u.first_name,
                }
                for u in users
            ])
        except Exception as e:
            return self.error(str(e), 500)
    
    async def stats(self, request):
        """GET /api/stats"""
        if not self.session:
            return self.error("Database not configured", 500)
        
        try:
            from domain.services import UserService
            from domain.repositories import UserRepository
            
            user_service = UserService(UserRepository(self.session))
            
            return self.success({
                "total_users": user_service.get_user_count(),
                "total_admins": len(user_service.get_admins()),
            })
        except Exception as e:
            return self.error(str(e), 500)
'''
    controllers_dir = project_path / "web" / "controllers"
    controllers_dir.mkdir(exist_ok=True)
    (controllers_dir / "__init__.py").write_text('"""\nWeb controllers\n"""\n')
    (controllers_dir / "api_controller.py").write_text(api_controller_content)
    
    # web/controllers/web_controller.py
    web_controller_content = '''"""
Web контроллер для обычных страниц
"""

from tgframework.web import Controller


class WebController(Controller):
    """Контроллер для веб-страниц"""
    
    def __init__(self, session=None):
        super().__init__()
        self.session = session
    
    async def index(self, request):
        """GET / - главная страница"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>My Bot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <h1>Welcome to My Bot</h1>
    <p>This is the web interface for your Telegram bot.</p>
    <ul>
        <li><a href="/api">API</a></li>
        <li><a href="/admin">Admin Panel</a></li>
    </ul>
</body>
</html>
        """
        return html
    
    async def about(self, request):
        """GET /about"""
        return self.json({
            "name": "My Bot",
            "description": "Created with TgFramework 3.0"
        })
'''
    (controllers_dir / "web_controller.py").write_text(web_controller_content)


def create_requirements_file(project_path: Path):
    """Создать requirements.txt"""
    requirements = """tgframework-bot>=3.0.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
psycopg2-binary>=2.9.0  # Если используете PostgreSQL
"""
    (project_path / "requirements.txt").write_text(requirements)


def create_readme_file(project_path: Path, project_name: str):
    """Создать README.md"""
    readme = f"""# {project_name}

Telegram бот, созданный с использованием TgFramework 3.0

## Установка

```bash
pip install -r requirements.txt
```

## Конфигурация

1. Скопируйте `.env.example` в `.env`
2. Отредактируйте `.env` и добавьте свой BOT_TOKEN
3. Настройте другие параметры по необходимости

## Запуск

```bash
python main.py
```

## Структура проекта

- `app/` - Обработчики, клавиатуры, middleware
- `domain/` - Domain модели, DTO, сервисы
- `infrastructure/` - База данных, внешние сервисы
- `web/` - Веб-сервер, админ-панель
- `main.py` - Точка входа

## Документация

Полная документация доступна на [GitHub](https://github.com/LankiSer/TgBotFramework)
"""
    (project_path / "README.md").write_text(readme)


def create_gitignore_file(project_path: Path):
    """Создать .gitignore"""
    gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# Logs
*.log

# OS
.DS_Store
Thumbs.db
"""
    (project_path / ".gitignore").write_text(gitignore)


def init_database():
    """Инициализировать базу данных и создать дефолтные миграции"""
    print("Инициализация базы данных...")
    
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    from .migration_templates import create_default_migrations
    from pathlib import Path
    
    try:
        # Загрузка конфигурации
        config = load_config()
        
        # Создание движка
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        # Создание дефолтных миграций
        migrations_path = Path("migrations")
        create_default_migrations(migrations_path)
        print(f"[SUCCESS] Дефолтные миграции созданы в {migrations_path}/")
        
        # Применение миграций
        migration_manager = MigrationManager(engine, str(migrations_path))
        migration_manager.migrate()
        
        print("[SUCCESS] База данных инициализирована")
    except Exception as e:
        print(f"[ERROR] Ошибка инициализации: {e}")


def run_migrations():
    """Запустить миграции (php artisan migrate)"""
    print("Запуск миграций...")
    
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    from pathlib import Path
    
    try:
        config = load_config()
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        migrations_path = Path("migrations")
        if not migrations_path.exists():
            print("[ERROR] Директория migrations не найдена. Запустите: tgframework init-db")
            return
        
        migration_manager = MigrationManager(engine, str(migrations_path))
        migration_manager.migrate()
        
        print("[SUCCESS] Миграции применены")
    except Exception as e:
        print(f"[ERROR] Ошибка миграции: {e}")


def rollback_migrations(steps: int = 1):
    """Откатить миграции (php artisan migrate:rollback)"""
    print(f"Откат последних {steps} батчей миграций...")
    
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    from pathlib import Path
    
    try:
        config = load_config()
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        migration_manager = MigrationManager(engine, "migrations")
        migration_manager.rollback(steps)
        
        print("[SUCCESS] Миграции откачены")
    except Exception as e:
        print(f"[ERROR] Ошибка отката: {e}")


def reset_migrations():
    """Откатить все миграции (php artisan migrate:reset)"""
    print("Откат всех миграций...")
    
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    
    try:
        config = load_config()
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        migration_manager = MigrationManager(engine, "migrations")
        migration_manager.reset()
        
        print("[SUCCESS] Все миграции откачены")
    except Exception as e:
        print(f"[ERROR] Ошибка сброса: {e}")


def refresh_migrations():
    """Откатить и применить заново (php artisan migrate:refresh)"""
    print("Обновление миграций...")
    
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    
    try:
        config = load_config()
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        migration_manager = MigrationManager(engine, "migrations")
        migration_manager.refresh()
        
        print("[SUCCESS] База данных обновлена")
    except Exception as e:
        print(f"[ERROR] Ошибка обновления: {e}")


def fresh_migrations():
    """Удалить все таблицы и применить миграции (php artisan migrate:fresh)"""
    print("Пересоздание базы данных...")
    
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    
    try:
        config = load_config()
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        migration_manager = MigrationManager(engine, "migrations")
        migration_manager.fresh()
        
        print("[SUCCESS] База данных пересоздана")
    except Exception as e:
        print(f"[ERROR] Ошибка пересоздания: {e}")


def migration_status():
    """Показать статус миграций (php artisan migrate:status)"""
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    
    try:
        config = load_config()
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        migration_manager = MigrationManager(engine, "migrations")
        migration_manager.status()
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")


def make_migration(name: str):
    """Создать новую миграцию (php artisan make:migration)"""
    from tgframework.core import load_config
    from tgframework.orm import create_engine, MigrationManager
    
    try:
        config = load_config()
        engine = create_engine(config.database.connection_string)
        engine.connect()
        
        migration_manager = MigrationManager(engine, "migrations")
        file_path = migration_manager.create_migration(name)
        
        print(f"[SUCCESS] Миграция создана: {file_path}")
    except Exception as e:
        print(f"[ERROR] Ошибка создания миграции: {e}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="TgFramework CLI")
    subparsers = parser.add_subparsers(dest="command", help="Команды")
    
    # create-project
    create_parser = subparsers.add_parser("create-project", help="Создать новый проект")
    create_parser.add_argument("name", help="Имя проекта")
    create_parser.add_argument("--output", "-o", help="Директория для создания проекта")
    
    # init-db
    subparsers.add_parser("init-db", help="Инициализировать базу данных и создать дефолтные миграции")
    
    # migrate
    subparsers.add_parser("migrate", help="Запустить миграции")
    
    # migrate:rollback
    rollback_parser = subparsers.add_parser("migrate:rollback", help="Откатить последний батч миграций")
    rollback_parser.add_argument("--steps", type=int, default=1, help="Количество батчей для отката")
    
    # migrate:reset
    subparsers.add_parser("migrate:reset", help="Откатить все миграции")
    
    # migrate:refresh
    subparsers.add_parser("migrate:refresh", help="Откатить и применить заново все миграции")
    
    # migrate:fresh
    subparsers.add_parser("migrate:fresh", help="Удалить все таблицы и применить миграции")
    
    # migrate:status
    subparsers.add_parser("migrate:status", help="Показать статус миграций")
    
    # make:migration
    make_migration_parser = subparsers.add_parser("make:migration", help="Создать новую миграцию")
    make_migration_parser.add_argument("name", help="Название миграции (например: create_products_table)")
    
    args = parser.parse_args()
    
    if args.command == "create-project":
        create_project(args.name, args.output)
    elif args.command == "init-db":
        init_database()
    elif args.command == "migrate":
        run_migrations()
    elif args.command == "migrate:rollback":
        rollback_migrations(args.steps)
    elif args.command == "migrate:reset":
        reset_migrations()
    elif args.command == "migrate:refresh":
        refresh_migrations()
    elif args.command == "migrate:fresh":
        fresh_migrations()
    elif args.command == "migrate:status":
        migration_status()
    elif args.command == "make:migration":
        make_migration(args.name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

