"""
Веб-сервер с админ-панелью
"""

from .server import WebServer
from .auth import TelegramAuth
from .routing import Router, Controller

__all__ = [
    "WebServer",
    "TelegramAuth",
    "Router",
    "Controller",
]

