"""
TgFramework - Полнофункциональный фреймворк для разработки Telegram ботов
"""

from .bot import Bot
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

__version__ = "2.0.1"
__all__ = [
    "Bot",
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
]

