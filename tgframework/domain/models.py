"""
Domain модели
"""

from datetime import datetime
from typing import Optional
from ..orm import Model, IntegerField, StringField, BooleanField, DateTimeField, TextField


class User(Model):
    """Модель пользователя"""
    
    _table_name = "users"
    
    user_id = IntegerField(primary_key=True)
    username = StringField(nullable=True)
    first_name = StringField(nullable=True)
    last_name = StringField(nullable=True)
    language_code = StringField(nullable=True)
    is_bot = BooleanField(default=False)
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    @property
    def full_name(self) -> str:
        """Получить полное имя"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.username or f"User {self.user_id}"


class Chat(Model):
    """Модель чата"""
    
    _table_name = "chats"
    
    chat_id = IntegerField(primary_key=True)
    chat_type = StringField()  # private, group, supergroup, channel
    title = StringField(nullable=True)
    username = StringField(nullable=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Message(Model):
    """Модель сообщения"""
    
    _table_name = "messages"
    
    id = IntegerField(primary_key=True, auto_increment=True)
    message_id = IntegerField()
    chat_id = IntegerField()
    user_id = IntegerField()
    text = TextField(nullable=True)
    created_at = DateTimeField(auto_now_add=True)


class UserState(Model):
    """Модель состояния пользователя"""
    
    _table_name = "user_states"
    
    user_id = IntegerField(primary_key=True)
    state = StringField()
    data = TextField(nullable=True)
    updated_at = DateTimeField(auto_now=True)

