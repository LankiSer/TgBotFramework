"""
Mini Apps модуль - поддержка Telegram Mini Apps с React/TypeScript
"""

from .validator import MiniAppValidator
from .renderer import ReactRenderer as LegacyReactRenderer, NextJSRenderer
from .react_renderer import ReactRenderer, get_telegram_user_photo_url

__all__ = [
    "MiniAppValidator",
    "ReactRenderer",
    "LegacyReactRenderer",
    "NextJSRenderer",
    "get_telegram_user_photo_url",
]
