"""
Веб-сервер с админ-панелью
"""

from .server import WebServer
from .admin import AdminPanel
from .auth import TelegramAuth
from .routing import Router, Controller

__all__ = [
    "WebServer",
    "AdminPanel",
    "TelegramAuth",
    "Router",
    "Controller",
]

