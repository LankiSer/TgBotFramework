"""
TgFramework - Полнофункциональный фреймворк для разработки Telegram ботов
"""

from .bot import Bot
from .database import Database
from .handlers import CommandHandler, CallbackHandler, MessageHandler
from .quiz import Quiz, QuizQuestion
from .keyboards import InlineKeyboardBuilder, ReplyKeyboardBuilder
from .state import State, StateMachine
from .middleware import Middleware, MiddlewareManager
from .utils import get_user_info, get_chat_info, format_text

__version__ = "1.0.0"
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
    "Middleware",
    "MiddlewareManager",
    "get_user_info",
    "get_chat_info",
    "format_text",
]

