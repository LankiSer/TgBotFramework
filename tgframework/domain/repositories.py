"""
Репозитории для работы с данными (Repository Pattern)
"""

from typing import List, Optional
from abc import ABC, abstractmethod
from ..orm import Session
from .models import User, Chat, Message, UserState
from .dto import UserDTO, ChatDTO, MessageDTO, CreateUserDTO, UpdateUserDTO


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def create(self, user_dto: CreateUserDTO) -> User:
        pass
    
    @abstractmethod
    def update(self, user_id: int, user_dto: UpdateUserDTO) -> Optional[User]:
        pass
    
    @abstractmethod
    def get_all(self, limit: Optional[int] = None) -> List[User]:
        pass
    
    @abstractmethod
    def get_admins(self) -> List[User]:
        pass
    
    @abstractmethod
    def count(self) -> int:
        pass


class UserRepository(IUserRepository):
    """Репозиторий пользователей"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.session.get(User, user_id)
    
    def create(self, user_dto: CreateUserDTO) -> User:
        """Создать пользователя"""
        user = User(
            user_id=user_dto.user_id,
            username=user_dto.username,
            first_name=user_dto.first_name,
            last_name=user_dto.last_name,
            language_code=user_dto.language_code,
            is_bot=user_dto.is_bot,
            is_admin=user_dto.is_admin,
        )
        return self.session.add(user)
    
    def update(self, user_id: int, user_dto: UpdateUserDTO) -> Optional[User]:
        """Обновить пользователя"""
        user = self.get_by_id(user_id)
        if not user:
            return None
        
        if user_dto.username is not None:
            user.username = user_dto.username
        if user_dto.first_name is not None:
            user.first_name = user_dto.first_name
        if user_dto.last_name is not None:
            user.last_name = user_dto.last_name
        if user_dto.language_code is not None:
            user.language_code = user_dto.language_code
        if user_dto.is_admin is not None:
            user.is_admin = user_dto.is_admin
        
        return self.session.update(user)
    
    def get_all(self, limit: Optional[int] = None) -> List[User]:
        """Получить всех пользователей"""
        query = self.session.query(User).order_by("created_at DESC")
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_admins(self) -> List[User]:
        """Получить всех администраторов"""
        return self.session.query(User).where(is_admin=True).all()
    
    def count(self) -> int:
        """Посчитать количество пользователей"""
        return self.session.query(User).count()


class IChatRepository(ABC):
    """Интерфейс репозитория чатов"""
    
    @abstractmethod
    def get_by_id(self, chat_id: int) -> Optional[Chat]:
        pass
    
    @abstractmethod
    def create(self, chat_dto: ChatDTO) -> Chat:
        pass


class ChatRepository(IChatRepository):
    """Репозиторий чатов"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, chat_id: int) -> Optional[Chat]:
        """Получить чат по ID"""
        return self.session.get(Chat, chat_id)
    
    def create(self, chat_dto: ChatDTO) -> Chat:
        """Создать чат"""
        chat = Chat(
            chat_id=chat_dto.chat_id,
            chat_type=chat_dto.chat_type,
            title=chat_dto.title,
            username=chat_dto.username,
        )
        return self.session.add(chat)


class IMessageRepository(ABC):
    """Интерфейс репозитория сообщений"""
    
    @abstractmethod
    def create(self, message_dto: MessageDTO) -> Message:
        pass
    
    @abstractmethod
    def get_by_chat(self, chat_id: int, limit: int = 100) -> List[Message]:
        pass


class MessageRepository(IMessageRepository):
    """Репозиторий сообщений"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, message_dto: MessageDTO) -> Message:
        """Создать сообщение"""
        message = Message(
            message_id=message_dto.message_id,
            chat_id=message_dto.chat_id,
            user_id=message_dto.user_id,
            text=message_dto.text,
        )
        return self.session.add(message)
    
    def get_by_chat(self, chat_id: int, limit: int = 100) -> List[Message]:
        """Получить сообщения чата"""
        return self.session.query(Message).where(chat_id=chat_id).order_by("created_at DESC").limit(limit).all()

