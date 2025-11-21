"""
TgFramework 3.0 - Полнофункциональный фреймворк для разработки Telegram ботов

Новые возможности:
- DDD/DTO архитектура
- Собственная ORM с поддержкой SQLite и PostgreSQL
- CLI для генерации проектов
- Веб-сервер с админ-панелью
- React/Next.js интеграция
- Telegram Mini Apps поддержка
- Конфигурация через .env
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

# Domain
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

# Bot
from .bot import TelegramBot
from .bot import TelegramBot as Bot  # Alias для обратной совместимости

# Старые модули (обратная совместимость)
from .database import Database
from .handlers import CommandHandler, CallbackHandler, MessageHandler
from .quiz import Quiz, QuizQuestion
from .keyboards import InlineKeyboardBuilder, ReplyKeyboardBuilder
from .state import State, StateMachine
from .fsm import State as FSMState, StatesGroup, FSMContext, state
from .middleware import Middleware, MiddlewareManager
from .filters import Filter, Filters
from .pagination import PaginationKeyboard, SimplePagination
from .rate_limiter import RateLimiter, TelegramRateLimiter
from .utils import get_user_info, get_chat_info, format_text

# Web
from .web import WebServer, AdminPanel, TelegramAuth

# Mini Apps
from .miniapp import MiniAppValidator, ReactRenderer, NextJSRenderer

__version__ = "3.0.0"

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
    
    # Bot
    "TelegramBot",
    "Bot",
    
    # Old modules (backward compatibility)
    "Database",
    "CommandHandler",
    "CallbackHandler",
    "MessageHandler",
    "Quiz",
    "QuizQuestion",
    "InlineKeyboardBuilder",
    "ReplyKeyboardBuilder",
    "State",
    "StateMachine",
    "FSMState",
    "StatesGroup",
    "FSMContext",
    "state",
    "Middleware",
    "MiddlewareManager",
    "Filter",
    "Filters",
    "PaginationKeyboard",
    "SimplePagination",
    "RateLimiter",
    "TelegramRateLimiter",
    "get_user_info",
    "get_chat_info",
    "format_text",
    
    # Web
    "WebServer",
    "AdminPanel",
    "TelegramAuth",
    
    # Mini Apps
    "MiniAppValidator",
    "ReactRenderer",
    "NextJSRenderer",
]
