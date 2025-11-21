"""
Поддержка Telegram Mini Apps
"""

from .validator import MiniAppValidator
from .renderer import ReactRenderer, NextJSRenderer

__all__ = [
    "MiniAppValidator",
    "ReactRenderer",
    "NextJSRenderer",
]

