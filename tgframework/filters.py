"""
Готовые фильтры для обработчиков (как в aiogram)
"""

from typing import Any, Dict, Optional, Callable


class Filter:
    """Базовый класс для фильтров"""
    
    def __call__(self, update: Dict[str, Any]) -> bool:
        """Проверить, соответствует ли update фильтру"""
        return self.check(update)
    
    def check(self, update: Dict[str, Any]) -> bool:
        """Проверить update"""
        raise NotImplementedError
    
    def __and__(self, other):
        """Оператор & для комбинации фильтров"""
        return AndFilter(self, other)
    
    def __or__(self, other):
        """Оператор | для комбинации фильтров"""
        return OrFilter(self, other)
    
    def __invert__(self):
        """Оператор ~ для инверсии фильтра"""
        return NotFilter(self)


class AndFilter(Filter):
    """Логическое И для фильтров"""
    
    def __init__(self, filter1: Filter, filter2: Filter):
        self.filter1 = filter1
        self.filter2 = filter2
    
    def check(self, update: Dict[str, Any]) -> bool:
        return self.filter1.check(update) and self.filter2.check(update)


class OrFilter(Filter):
    """Логическое ИЛИ для фильтров"""
    
    def __init__(self, filter1: Filter, filter2: Filter):
        self.filter1 = filter1
        self.filter2 = filter2
    
    def check(self, update: Dict[str, Any]) -> bool:
        return self.filter1.check(update) or self.filter2.check(update)


class NotFilter(Filter):
    """Инверсия фильтра"""
    
    def __init__(self, filter_obj: Filter):
        self.filter_obj = filter_obj
    
    def check(self, update: Dict[str, Any]) -> bool:
        return not self.filter_obj.check(update)


class Filters:
    """Набор готовых фильтров"""
    
    class Text(Filter):
        """Фильтр для текстовых сообщений"""
        
        def __init__(self, text: Optional[str] = None):
            self.text = text
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            message_text = message.get("text", "")
            
            if self.text is None:
                return bool(message_text)
            return message_text == self.text
    
    class TextContains(Filter):
        """Фильтр для сообщений содержащих текст"""
        
        def __init__(self, text: str):
            self.text = text
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            message_text = message.get("text", "")
            return self.text in message_text
    
    class TextStartswith(Filter):
        """Фильтр для сообщений начинающихся с текста"""
        
        def __init__(self, text: str):
            self.text = text
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            message_text = message.get("text", "")
            return message_text.startswith(self.text)
    
    class Command(Filter):
        """Фильтр для команд"""
        
        def __init__(self, command: Optional[str] = None):
            self.command = command.lower() if command else None
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            text = message.get("text", "")
            
            if not text or not text.startswith("/"):
                return False
            
            command = text.split()[0][1:].lower()
            
            if self.command is None:
                return True
            return command == self.command
    
    class CallbackQuery(Filter):
        """Фильтр для callback query"""
        
        def __init__(self, data: Optional[str] = None):
            self.data = data
        
        def check(self, update: Dict[str, Any]) -> bool:
            if "callback_query" not in update:
                return False
            
            callback_data = update["callback_query"].get("data", "")
            
            if self.data is None:
                return True
            
            if isinstance(self.data, str):
                return callback_data.startswith(self.data)
            return callback_data == self.data
    
    class Photo(Filter):
        """Фильтр для фото"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "photo" in message
    
    class Document(Filter):
        """Фильтр для документов"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "document" in message
    
    class Video(Filter):
        """Фильтр для видео"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "video" in message
    
    class Audio(Filter):
        """Фильтр для аудио"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "audio" in message
    
    class Voice(Filter):
        """Фильтр для голосовых сообщений"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "voice" in message
    
    class Contact(Filter):
        """Фильтр для контактов"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "contact" in message
    
    class Location(Filter):
        """Фильтр для местоположения"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "location" in message
    
    class PrivateChat(Filter):
        """Фильтр для приватных чатов"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            chat = message.get("chat", {})
            return chat.get("type") == "private"
    
    class GroupChat(Filter):
        """Фильтр для групповых чатов"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            chat = message.get("chat", {})
            chat_type = chat.get("type")
            return chat_type in ("group", "supergroup")
    
    class User(Filter):
        """Фильтр для определенного пользователя"""
        
        def __init__(self, user_id: int):
            self.user_id = user_id
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            user = message.get("from", {})
            return user.get("id") == self.user_id
    
    class Forwarded(Filter):
        """Фильтр для пересланных сообщений"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "forward_from" in message or "forward_from_chat" in message
    
    class Reply(Filter):
        """Фильтр для ответов на сообщения"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            return "reply_to_message" in message
    
    class IsAdmin(Filter):
        """Фильтр для проверки администратора (требует bot в context)"""
        
        def check(self, update: Dict[str, Any]) -> bool:
            message = update.get("message", {})
            user = message.get("from", {})
            user_id = user.get("id")
            
            if not user_id:
                return False
            
            # Получаем bot из context (должен быть установлен middleware)
            # Это будет работать только если bot доступен через context
            return False  # По умолчанию False, требует доступа к bot


# Создаем экземпляры для удобного использования
text = Filters.Text()
photo = Filters.Photo()
document = Filters.Document()
video = Filters.Video()
audio = Filters.Audio()
voice = Filters.Voice()
contact = Filters.Contact()
location = Filters.Location()
private = Filters.PrivateChat()
group = Filters.GroupChat()
forwarded = Filters.Forwarded()
reply = Filters.Reply()

