"""
Core модуль фреймворка с базовыми абстракциями
"""

from .config import Config, load_config
from .exceptions import *

__all__ = [
    "Config",
    "load_config",
]

