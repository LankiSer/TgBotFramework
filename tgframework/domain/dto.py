"""
Data Transfer Objects (DTO)
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserDTO:
    """DTO для пользователя"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_bot: bool = False
    is_admin: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Получить полное имя"""
        parts = []
        if self.first_name:
            parts.append(self.first_name)
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts) if parts else self.username or f"User {self.user_id}"


@dataclass
class CreateUserDTO:
    """DTO для создания пользователя"""
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_bot: bool = False
    is_admin: bool = False


@dataclass
class UpdateUserDTO:
    """DTO для обновления пользователя"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_admin: Optional[bool] = None


@dataclass
class ChatDTO:
    """DTO для чата"""
    chat_id: int
    chat_type: str
    title: Optional[str] = None
    username: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class MessageDTO:
    """DTO для сообщения"""
    message_id: int
    chat_id: int
    user_id: int
    text: Optional[str] = None
    created_at: Optional[datetime] = None

