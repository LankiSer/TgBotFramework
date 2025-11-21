"""
Domain сервисы (бизнес-логика)
"""

from typing import List, Optional
from .models import User, Chat, Message
from .dto import UserDTO, CreateUserDTO, UpdateUserDTO, ChatDTO, MessageDTO
from .repositories import UserRepository, ChatRepository, MessageRepository


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, user_repository: UserRepository):
        self.repository = user_repository
    
    def get_user(self, user_id: int) -> Optional[UserDTO]:
        """Получить пользователя"""
        user = self.repository.get_by_id(user_id)
        if user:
            return self._to_dto(user)
        return None
    
    def create_user(self, user_dto: CreateUserDTO) -> UserDTO:
        """Создать пользователя"""
        user = self.repository.create(user_dto)
        return self._to_dto(user)
    
    def update_user(self, user_id: int, user_dto: UpdateUserDTO) -> Optional[UserDTO]:
        """Обновить пользователя"""
        user = self.repository.update(user_id, user_dto)
        if user:
            return self._to_dto(user)
        return None
    
    def get_all_users(self, limit: Optional[int] = None) -> List[UserDTO]:
        """Получить всех пользователей"""
        users = self.repository.get_all(limit)
        return [self._to_dto(user) for user in users]
    
    def get_admins(self) -> List[UserDTO]:
        """Получить администраторов"""
        users = self.repository.get_admins()
        return [self._to_dto(user) for user in users]
    
    def set_admin(self, user_id: int, is_admin: bool) -> Optional[UserDTO]:
        """Установить статус администратора"""
        return self.update_user(user_id, UpdateUserDTO(is_admin=is_admin))
    
    def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        user = self.repository.get_by_id(user_id)
        return user.is_admin if user else False
    
    def get_user_count(self) -> int:
        """Получить количество пользователей"""
        return self.repository.count()
    
    def _to_dto(self, user: User) -> UserDTO:
        """Преобразовать модель в DTO"""
        return UserDTO(
            user_id=user.user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code,
            is_bot=user.is_bot,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class ChatService:
    """Сервис для работы с чатами"""
    
    def __init__(self, chat_repository: ChatRepository):
        self.repository = chat_repository
    
    def get_chat(self, chat_id: int) -> Optional[ChatDTO]:
        """Получить чат"""
        chat = self.repository.get_by_id(chat_id)
        if chat:
            return self._to_dto(chat)
        return None
    
    def create_chat(self, chat_dto: ChatDTO) -> ChatDTO:
        """Создать чат"""
        chat = self.repository.create(chat_dto)
        return self._to_dto(chat)
    
    def _to_dto(self, chat: Chat) -> ChatDTO:
        """Преобразовать модель в DTO"""
        return ChatDTO(
            chat_id=chat.chat_id,
            chat_type=chat.chat_type,
            title=chat.title,
            username=chat.username,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
        )


class MessageService:
    """Сервис для работы с сообщениями"""
    
    def __init__(self, message_repository: MessageRepository):
        self.repository = message_repository
    
    def create_message(self, message_dto: MessageDTO) -> MessageDTO:
        """Создать сообщение"""
        message = self.repository.create(message_dto)
        return self._to_dto(message)
    
    def get_chat_messages(self, chat_id: int, limit: int = 100) -> List[MessageDTO]:
        """Получить сообщения чата"""
        messages = self.repository.get_by_chat(chat_id, limit)
        return [self._to_dto(message) for message in messages]
    
    def _to_dto(self, message: Message) -> MessageDTO:
        """Преобразовать модель в DTO"""
        return MessageDTO(
            message_id=message.message_id,
            chat_id=message.chat_id,
            user_id=message.user_id,
            text=message.text,
            created_at=message.created_at,
        )

