"""
Основной класс бота с поддержкой polling
"""

import asyncio
import json
import time
from typing import Any, Callable, Dict, List, Optional
import aiohttp
from .database import Database
from .handlers import CommandHandler, CallbackHandler, MessageHandler
from .state import StateMachine
from .middleware import MiddlewareManager
from .utils import get_user_info, get_chat_info, parse_command


class Bot:
    """Основной класс бота для Telegram"""
    
    def __init__(self, token: str, db_path: str = "bot.db"):
        """
        Инициализация бота
        
        Args:
            token: Токен бота от @BotFather
            db_path: Путь к файлу базы данных
        """
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.db = Database(db_path)
        self.state_machine = StateMachine(self.db)
        self.middleware_manager = MiddlewareManager()
        
        # Обработчики
        self.command_handlers: Dict[str, CommandHandler] = {}
        self.callback_handlers: List[CallbackHandler] = []
        self.message_handlers: List[MessageHandler] = []
        
        # Настройки polling
        self.running = False
        self.offset = 0
        self.timeout = 30
        self.limit = 100
        
        # Сессия для HTTP запросов
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _make_request(self, method: str, **params) -> Dict[str, Any]:
        """
        Выполнить запрос к API Telegram
        
        Args:
            method: Название метода API
            **params: Параметры запроса
            
        Returns:
            Ответ от API
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.api_url}/{method}"
        
        async with self.session.post(url, json=params) as response:
            result = await response.json()
            if not result.get("ok"):
                raise Exception(f"API Error: {result.get('description')}")
            return result.get("result")
    
    async def send_message(self, chat_id: int, text: str, 
                          reply_markup: Optional[Dict] = None,
                          parse_mode: Optional[str] = None,
                          reply_to_message_id: Optional[int] = None,
                          **kwargs) -> Dict[str, Any]:
        """
        Отправить сообщение
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            reply_markup: Клавиатура
            parse_mode: Режим парсинга (HTML, Markdown, MarkdownV2)
            reply_to_message_id: ID сообщения для ответа
            **kwargs: Дополнительные параметры
            
        Returns:
            Отправленное сообщение
        """
        params = {
            "chat_id": chat_id,
            "text": text,
            **kwargs
        }
        
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        if parse_mode:
            params["parse_mode"] = parse_mode
        if reply_to_message_id:
            params["reply_to_message_id"] = reply_to_message_id
        
        return await self._make_request("sendMessage", **params)
    
    async def edit_message_text(self, chat_id: int, message_id: int, text: str,
                                reply_markup: Optional[Dict] = None,
                                parse_mode: Optional[str] = None,
                                **kwargs) -> Dict[str, Any]:
        """
        Редактировать текст сообщения
        
        Args:
            chat_id: ID чата
            message_id: ID сообщения
            text: Новый текст
            reply_markup: Новая клавиатура
            parse_mode: Режим парсинга
            **kwargs: Дополнительные параметры
            
        Returns:
            Отредактированное сообщение
        """
        params = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            **kwargs
        }
        
        if reply_markup:
            params["reply_markup"] = json.dumps(reply_markup)
        if parse_mode:
            params["parse_mode"] = parse_mode
        
        return await self._make_request("editMessageText", **params)
    
    async def answer_callback_query(self, callback_query_id: str, 
                                    text: Optional[str] = None,
                                    show_alert: bool = False,
                                    **kwargs) -> bool:
        """
        Ответить на callback query
        
        Args:
            callback_query_id: ID callback query
            text: Текст ответа
            show_alert: Показать ли alert вместо уведомления
            **kwargs: Дополнительные параметры
            
        Returns:
            True если успешно
        """
        params = {
            "callback_query_id": callback_query_id,
            **kwargs
        }
        
        if text:
            params["text"] = text
        if show_alert:
            params["show_alert"] = show_alert
        
        return await self._make_request("answerCallbackQuery", **params)
    
    async def delete_message(self, chat_id: int, message_id: int) -> bool:
        """
        Удалить сообщение
        
        Args:
            chat_id: ID чата
            message_id: ID сообщения
            
        Returns:
            True если успешно
        """
        return await self._make_request("deleteMessage", chat_id=chat_id, message_id=message_id)
    
    async def get_updates(self) -> List[Dict[str, Any]]:
        """
        Получить обновления от Telegram
        
        Returns:
            Список обновлений
        """
        params = {
            "offset": self.offset,
            "timeout": self.timeout,
            "limit": self.limit
        }
        
        updates = await self._make_request("getUpdates", **params)
        return updates or []
    
    def register_command(self, command: str = None, handler: Callable = None, description: Optional[str] = None):
        """
        Зарегистрировать обработчик команды
        
        Можно использовать как декоратор:
            @bot.register_command("start")
            async def start(update, context):
                ...
        
        Или напрямую:
            bot.register_command("start", handler, "Описание")
        
        Args:
            command: Название команды (без /)
            handler: Функция-обработчик (если используется как декоратор)
            description: Описание команды
        """
        if handler is None:
            # Используется как декоратор
            def decorator(func: Callable):
                self.command_handlers[command.lower()] = CommandHandler(command, func, description)
                return func
            return decorator
        else:
            # Используется напрямую
            self.command_handlers[command.lower()] = CommandHandler(command, handler, description)
    
    def register_callback(self, pattern: str = None, handler: Callable = None):
        """
        Зарегистрировать обработчик callback
        
        Можно использовать как декоратор:
            @bot.register_callback("button_")
            async def button_handler(update, context):
                ...
        
        Или напрямую:
            bot.register_callback("button_", handler)
        
        Args:
            pattern: Паттерн для callback_data
            handler: Функция-обработчик (если используется как декоратор)
        """
        if handler is None:
            # Используется как декоратор
            def decorator(func: Callable):
                self.callback_handlers.append(CallbackHandler(pattern, func))
                return func
            return decorator
        else:
            # Используется напрямую
            self.callback_handlers.append(CallbackHandler(pattern, handler))
    
    def register_message_handler(self, handler: Callable = None, filters: Optional[Callable] = None):
        """
        Зарегистрировать обработчик сообщений
        
        Можно использовать как декоратор:
            @bot.register_message_handler(filters=lambda u: u.get("message", {}).get("text"))
            async def text_handler(update, context):
                ...
        
        Или напрямую:
            bot.register_message_handler(handler, filters)
        
        Args:
            handler: Функция-обработчик (если используется как декоратор)
            filters: Функция-фильтр
        """
        if handler is None:
            # Используется как декоратор
            def decorator(func: Callable):
                self.message_handlers.append(MessageHandler(func, filters))
                return func
            return decorator
        else:
            # Используется напрямую
            self.message_handlers.append(MessageHandler(handler, filters))
    
    async def _process_update(self, update: Dict[str, Any]):
        """
        Обработать одно обновление
        
        Args:
            update: Update от Telegram
        """
        context = {
            "bot": self,
            "db": self.db,
            "state_machine": self.state_machine,
        }
        
        # Обработка через middleware
        should_continue = await self.middleware_manager.process(update, context)
        if not should_continue:
            return
        
        # Обработка callback query
        if "callback_query" in update:
            callback_query = update["callback_query"]
            callback_data = callback_query.get("data", "")
            
            # Сохранение пользователя
            if "from" in callback_query:
                user = callback_query["from"]
                self.db.add_user(
                    user["id"],
                    user.get("username"),
                    user.get("first_name"),
                    user.get("last_name"),
                    user.get("language_code"),
                    user.get("is_bot", False)
                )
            
            # Поиск обработчика
            for handler in self.callback_handlers:
                if handler.matches(callback_data):
                    context["callback_data"] = callback_data
                    context["callback_query"] = callback_query
                    await handler.handle(update, context)
                    return
        
        # Обработка сообщения
        if "message" in update:
            message = update["message"]
            user = message.get("from")
            chat = message.get("chat")
            text = message.get("text")
            
            # Сохранение пользователя и чата
            if user:
                self.db.add_user(
                    user["id"],
                    user.get("username"),
                    user.get("first_name"),
                    user.get("last_name"),
                    user.get("language_code"),
                    user.get("is_bot", False)
                )
            
            if chat:
                self.db.add_chat(
                    chat["id"],
                    chat.get("type", "private"),
                    chat.get("title"),
                    chat.get("username")
                )
            
            # Сохранение сообщения
            if user and chat and "message_id" in message:
                self.db.save_message(
                    message["message_id"],
                    chat["id"],
                    user["id"],
                    text
                )
            
            context["user"] = user
            context["chat"] = chat
            context["message"] = message
            context["text"] = text
            
            # Обработка команды
            if text and text.startswith("/"):
                command, args = parse_command(text)
                context["command"] = command
                context["args"] = args
                
                if command in self.command_handlers:
                    await self.command_handlers[command].handle(update, context)
                    return
            
            # Обработка обычного сообщения
            for handler in self.message_handlers:
                if handler.should_handle(update):
                    await handler.handle(update, context)
                    return
    
    async def _polling_loop(self):
        """Основной цикл polling"""
        while self.running:
            try:
                updates = await self.get_updates()
                
                for update in updates:
                    update_id = update.get("update_id")
                    if update_id:
                        self.offset = update_id + 1
                    
                    await self._process_update(update)
                
            except Exception as e:
                print(f"Ошибка при обработке обновлений: {e}")
                await asyncio.sleep(5)
    
    async def start_polling(self):
        """Запустить polling"""
        self.running = True
        print(f"Бот запущен и ожидает обновления...")
        
        try:
            await self._polling_loop()
        except KeyboardInterrupt:
            print("\nОстановка бота...")
        finally:
            await self.stop()
    
    async def stop(self):
        """Остановить бота"""
        self.running = False
        if self.session:
            await self.session.close()
        self.db.close()
        print("Бот остановлен.")
    
    def run(self):
        """Запустить бота (синхронный метод)"""
        try:
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            print("\nОстановка бота...")

