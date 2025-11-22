"""
TgFramework 3.0 - Полнофункциональный фреймворк для разработки Telegram ботов

Архитектура:
- Core: Конфигурация, исключения
- ORM: База данных (SQLite/PostgreSQL)
- Domain: Модели, DTO, сервисы, репозитории (DDD)
- Application: Handlers, keyboards, filters, middleware
- Infrastructure: Rate limiter, utils
- Features: Quiz, FSM
- Bot: Telegram бот
- Web: Веб-сервер, роутинг, контроллеры
- Mini Apps: Поддержка Telegram Mini Apps
- CLI: Генератор проектов, миграции
"""

# Core
from .core import Config, load_config

# ORM
from .orm import (
    DatabaseEngine,
    create_engine,
    Model,
    Field,
    IntegerField,
    StringField,
    BooleanField,
    DateTimeField,
    TextField,
    ForeignKey,
    QueryBuilder,
    Session,
    Migration,
    MigrationManager,
)

# Domain (DDD)
from .domain import (
    User,
    Chat,
    Message,
    UserState,
    UserDTO,
    ChatDTO,
    MessageDTO,
    CreateUserDTO,
    UpdateUserDTO,
    UserRepository,
    ChatRepository,
    MessageRepository,
    UserService,
    ChatService,
    MessageService,
)

# Application
from .application import (
    CommandHandler,
    CallbackHandler,
    MessageHandler,
    InlineKeyboardBuilder,
    ReplyKeyboardBuilder,
    Filter,
    Filters,
    Middleware,
    MiddlewareManager,
    StateMachine,
    State,
    PaginationKeyboard,
    SimplePagination,
)

# Infrastructure
from .infrastructure import (
    RateLimiter,
    TelegramRateLimiter,
    get_user_info,
    get_chat_info,
    format_text,
    parse_command,
    escape_html,
    escape_markdown,
)

# Features
from .features import (
    Quiz,
    QuizQuestion,
    FSMState,
    StatesGroup,
    FSMContext,
    state,
)

# Bot
from .bot import TelegramBot
from .bot import TelegramBot as Bot  # Alias

# Web
from .web import WebServer, TelegramAuth, Router, Controller

# Mini Apps
from .miniapp import MiniAppValidator, ReactRenderer, NextJSRenderer, get_telegram_user_photo_url

# Backward compatibility - Database (deprecated, use ORM)
from .orm import Session as Database  # Temporary alias

__version__ = "3.1.2"

__all__ = [
    # Core
    "Config",
    "load_config",
    
    # ORM
    "DatabaseEngine",
    "create_engine",
    "Model",
    "Field",
    "IntegerField",
    "StringField",
    "BooleanField",
    "DateTimeField",
    "TextField",
    "ForeignKey",
    "QueryBuilder",
    "Session",
    "Migration",
    "MigrationManager",
    "Database",  # Deprecated
    
    # Domain
    "User",
    "Chat",
    "Message",
    "UserState",
    "UserDTO",
    "ChatDTO",
    "MessageDTO",
    "CreateUserDTO",
    "UpdateUserDTO",
    "UserRepository",
    "ChatRepository",
    "MessageRepository",
    "UserService",
    "ChatService",
    "MessageService",
    
    # Application
    "CommandHandler",
    "CallbackHandler",
    "MessageHandler",
    "InlineKeyboardBuilder",
    "ReplyKeyboardBuilder",
    "Filter",
    "Filters",
    "Middleware",
    "MiddlewareManager",
    "StateMachine",
    "State",
    "PaginationKeyboard",
    "SimplePagination",
    
    # Infrastructure
    "RateLimiter",
    "TelegramRateLimiter",
    "get_user_info",
    "get_chat_info",
    "format_text",
    "parse_command",
    "escape_html",
    "escape_markdown",
    
    # Features
    "Quiz",
    "QuizQuestion",
    "FSMState",
    "StatesGroup",
    "FSMContext",
    "state",
    
    # Bot
    "TelegramBot",
    "Bot",
    
    # Web
    "WebServer",
    "TelegramAuth",
    "Router",
    "Controller",
    
    # Mini Apps
    "MiniAppValidator",
    "ReactRenderer",
    "NextJSRenderer",
    "get_telegram_user_photo_url",
]
