"""
Основной класс бота с поддержкой polling и webhook
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional
import aiohttp
from aiohttp import web

from ..handlers import CommandHandler, CallbackHandler, MessageHandler
from ..state import StateMachine
from ..middleware import MiddlewareManager
from ..rate_limiter import TelegramRateLimiter
from ..utils import parse_command

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """Основной класс бота для Telegram"""
    
    def __init__(self, token: str, session=None):
        """
        Инициализация бота
        
        Args:
            token: Токен бота от @BotFather
            session: Сессия БД (опционально)
        """
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}"
        self.db_session = session
        self.state_machine = None
        self.middleware_manager = MiddlewareManager()
        self.rate_limiter = TelegramRateLimiter()
        
        # Обработчики
        self.command_handlers: Dict[str, CommandHandler] = {}
        self.callback_handlers: List[CallbackHandler] = []
        self.message_handlers: List[MessageHandler] = []
        self.state_handlers: Dict[str, List[Callable]] = {}
        
        # Настройки polling
        self.running = False
        self.offset = 0
        self.timeout = 30
        self.limit = 100
        
        # Webhook настройки
        self.webhook_url: Optional[str] = None
        self.webhook_path: Optional[str] = None
        self.webhook_server: Optional[web.Application] = None
        
        # Обработчики ошибок
        self.error_handlers: List[Callable] = []
        
        # Сессия для HTTP запросов
        self.session: Optional[aiohttp.ClientSession] = None
    
    def set_state_machine(self, state_machine: StateMachine):
        """Установить state machine"""
        self.state_machine = state_machine
    
    async def _make_request(self, method: str, retries: int = 3, **params) -> Dict[str, Any]:
        """
        Выполнить запрос к API Telegram с обработкой ошибок и retry
        
        Args:
            method: Название метода API
            retries: Количество попыток при ошибке
            **params: Параметры запроса
            
        Returns:
            Ответ от API
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.api_url}/{method}"
        
        for attempt in range(retries):
            try:
                async with self.session.post(url, json=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    result = await response.json()
                    
                    if not result.get("ok"):
                        error_code = result.get("error_code", 0)
                        description = result.get("description", "Unknown error")
                        
                        # Обработка rate limit
                        if error_code == 429:
                            retry_after = result.get("parameters", {}).get("retry_after", 1)
                            logger.warning(f"Rate limit exceeded. Waiting {retry_after} seconds...")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        # Обработка других ошибок
                        error = Exception(f"API Error {error_code}: {description}")
                        await self._handle_error(error, method=method, params=params)
                        raise error
                    
                    return result.get("result")
                    
            except asyncio.TimeoutError:
                if attempt < retries - 1:
                    logger.warning(f"Timeout on attempt {attempt + 1}/{retries}. Retrying...")
                    await asyncio.sleep(1)
                    continue
                raise
            except Exception as e:
                if attempt < retries - 1:
                    logger.warning(f"Error on attempt {attempt + 1}/{retries}: {e}. Retrying...")
                    await asyncio.sleep(1)
                    continue
                await self._handle_error(e, method=method, params=params)
                raise
        
        raise Exception(f"Failed to execute {method} after {retries} attempts")
    
    async def _handle_error(self, error: Exception, **context):
        """Обработать ошибку через зарегистрированные обработчики"""
        for handler in self.error_handlers:
            try:
                await handler(error, context)
            except Exception as e:
                logger.error(f"Error in error handler: {e}")
    
    def register_error_handler(self, handler: Callable):
        """Зарегистрировать обработчик ошибок"""
        self.error_handlers.append(handler)
    
    async def send_message(self, chat_id: int, text: str, 
                          reply_markup: Optional[Dict] = None,
                          parse_mode: Optional[str] = None,
                          reply_to_message_id: Optional[int] = None,
                          rate_limit: bool = True,
                          **kwargs) -> Dict[str, Any]:
        """
        Отправить сообщение с rate limiting
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
            reply_markup: Клавиатура
            parse_mode: Режим парсинга (HTML, Markdown, MarkdownV2)
            reply_to_message_id: ID сообщения для ответа
            rate_limit: Применить rate limiting
            **kwargs: Дополнительные параметры
            
        Returns:
            Отправленное сообщение
        """
        if rate_limit:
            user_id = kwargs.get("user_id") if isinstance(chat_id, int) and chat_id > 0 else None
            await self.rate_limiter.wait_message(user_id)
        
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
        """Редактировать текст сообщения"""
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
        """Ответить на callback query"""
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
        """Удалить сообщение"""
        return await self._make_request("deleteMessage", chat_id=chat_id, message_id=message_id)
    
    async def get_updates(self) -> List[Dict[str, Any]]:
        """Получить обновления от Telegram"""
        params = {
            "offset": self.offset,
            "timeout": self.timeout,
            "limit": self.limit
        }
        
        updates = await self._make_request("getUpdates", **params)
        return updates or []
    
    def register_command(self, command: str = None, handler: Callable = None, description: Optional[str] = None):
        """Зарегистрировать обработчик команды"""
        if handler is None:
            def decorator(func: Callable):
                self.command_handlers[command.lower()] = CommandHandler(command, func, description)
                return func
            return decorator
        else:
            self.command_handlers[command.lower()] = CommandHandler(command, handler, description)
    
    def register_callback(self, pattern: str = None, handler: Callable = None):
        """Зарегистрировать обработчик callback"""
        if handler is None:
            def decorator(func: Callable):
                self.callback_handlers.append(CallbackHandler(pattern, func))
                return func
            return decorator
        else:
            self.callback_handlers.append(CallbackHandler(pattern, handler))
    
    def register_message_handler(self, handler: Callable = None, filters=None):
        """Зарегистрировать обработчик сообщений"""
        if handler is None and filters is None:
            def decorator(func: Callable):
                self.message_handlers.append(MessageHandler(func, None))
                return func
            return decorator
        
        if handler is None and filters is not None:
            def decorator(func: Callable):
                if hasattr(filters, 'check'):
                    filter_func = filters.check
                else:
                    filter_func = filters
                self.message_handlers.append(MessageHandler(func, filter_func))
                return func
            return decorator
        
        if handler is not None and callable(handler) and filters is None:
            import inspect
            try:
                sig = inspect.signature(handler)
                params = list(sig.parameters.values())
                
                if len(params) == 1:
                    def decorator(func: Callable):
                        if hasattr(handler, 'check'):
                            filter_func = handler.check
                        else:
                            filter_func = handler
                        self.message_handlers.append(MessageHandler(func, filter_func))
                        return func
                    return decorator
            except (ValueError, TypeError):
                pass
        
        if handler is not None and callable(handler):
            if hasattr(filters, 'check'):
                filter_func = filters.check
            else:
                filter_func = filters
            self.message_handlers.append(MessageHandler(handler, filter_func))
            return
        
        raise TypeError("register_message_handler: incorrect usage")
    
    async def _process_update(self, update: Dict[str, Any]):
        """Обработать одно обновление"""
        context = {
            "bot": self,
            "db_session": self.db_session,
            "state_machine": self.state_machine,
        }
        
        # Обработка через middleware
        should_continue = await self.middleware_manager.process(update, context)
        if not should_continue:
            return
        
        # Обработка callback query
        if "callback_query" in update:
            await self._handle_callback(update, context)
            return
        
        # Обработка сообщения
        if "message" in update:
            await self._handle_message(update, context)
            return
    
    async def _handle_callback(self, update: Dict[str, Any], context: Dict[str, Any]):
        """Обработать callback query"""
        callback_query = update["callback_query"]
        callback_data = callback_query.get("data", "")
        
        context["callback_data"] = callback_data
        context["callback_query"] = callback_query
        
        for handler in self.callback_handlers:
            if handler.matches(callback_data):
                await handler.handle(update, context)
                return
    
    async def _handle_message(self, update: Dict[str, Any], context: Dict[str, Any]):
        """Обработать сообщение"""
        message = update["message"]
        user = message.get("from")
        chat = message.get("chat")
        text = message.get("text")
        
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
        
        # Обработка FSM состояний
        if user and text and self.state_machine:
            user_id = user["id"]
            current_state = self.state_machine.get_state(user_id)
            
            if current_state and current_state in self.state_handlers:
                for handler in self.state_handlers[current_state]:
                    try:
                        await handler(update, context)
                        return
                    except Exception as e:
                        logger.error(f"Error in state handler: {e}", exc_info=True)
                        await self._handle_error(e, update=update)
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
                
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"Error in polling loop: {e}", exc_info=True)
                await self._handle_error(e)
                await asyncio.sleep(5)
    
    async def start_polling(self):
        """Запустить polling"""
        self.running = True
        logger.info("Bot started in polling mode")
        
        try:
            await self._polling_loop()
        except KeyboardInterrupt:
            logger.info("Received stop signal")
        finally:
            await self.stop()
    
    async def set_webhook(self, url: str, secret_token: Optional[str] = None):
        """Установить webhook"""
        params = {"url": url}
        if secret_token:
            params["secret_token"] = secret_token
        
        result = await self._make_request("setWebhook", **params)
        self.webhook_url = url
        logger.info(f"Webhook set: {url}")
        return result
    
    async def delete_webhook(self, drop_pending_updates: bool = False):
        """Удалить webhook"""
        params = {}
        if drop_pending_updates:
            params["drop_pending_updates"] = True
        
        result = await self._make_request("deleteWebhook", **params)
        self.webhook_url = None
        logger.info("Webhook deleted")
        return result
    
    async def start_webhook(self, host: str = "0.0.0.0", port: int = 8080,
                           path: str = "/webhook", secret_token: Optional[str] = None):
        """Запустить webhook сервер"""
        app = web.Application()
        self.webhook_path = path
        
        async def webhook_handler(request):
            if secret_token:
                token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if token != secret_token:
                    logger.warning("Invalid secret token")
                    return web.Response(status=403)
            
            try:
                update = await request.json()
                await self._process_update(update)
                return web.Response(status=200)
            except Exception as e:
                logger.error(f"Error processing webhook: {e}", exc_info=True)
                await self._handle_error(e, request=request)
                return web.Response(status=500)
        
        app.router.add_post(path, webhook_handler)
        self.webhook_server = app
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"Webhook server started on {host}:{port}{path}")
        
        webhook_url = f"https://{host}:{port}{path}" if host != "0.0.0.0" else f"http://your-domain.com{path}"
        await self.set_webhook(webhook_url, secret_token)
        
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            logger.info("Stopping webhook server...")
        finally:
            await runner.cleanup()
            await self.delete_webhook()
    
    async def stop(self):
        """Остановить бота"""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("Bot stopped")
    
    def run(self):
        """Запустить бота (синхронный метод)"""
        try:
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            logger.info("Stopping bot...")


# Alias для обратной совместимости
Bot = TelegramBot

