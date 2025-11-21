"""
Веб-сервер на aiohttp с роутингом в стиле Laravel
"""

import asyncio
import logging
from typing import Optional
from aiohttp import web
from ..core import Config
from ..orm import Session
from .routing import Router
from .controllers import ApiController, MiniAppController, AdminController
from .auth import TelegramAuth

logger = logging.getLogger(__name__)


class WebServer:
    """Веб-сервер для админ-панели и API"""
    
    def __init__(self, config: Config, session: Session, bot=None):
        self.config = config
        self.session = session
        self.bot = bot
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.router = Router()
        
        # Компоненты
        self.auth = TelegramAuth(config.bot.token)
        
        # Контроллеры
        self.api_controller = ApiController(session, bot)
        self.miniapp_controller = MiniAppController(config, session)
        self.admin_controller = AdminController(session, self.auth) if config.web.admin_enabled else None
        
        self._setup_routes()
        self._setup_middlewares()
    
    def _setup_routes(self):
        """Настроить маршруты в стиле Laravel"""
        # Статические файлы
        self.app.router.add_static('/static/', path='web/static/', name='static')
        
        # API routes
        with self.router.group(prefix="/api"):
            self.router.get("", self.api_controller.index, name="api.index")
            self.router.get("/users", self.api_controller.users, name="api.users")
            self.router.get("/users/{id}", self.api_controller.user_detail, name="api.user.detail")
            self.router.get("/stats", self.api_controller.stats, name="api.stats")
            self.router.post("/send", self.api_controller.send_message, name="api.send")
        
        # Mini App routes
        with self.router.group(prefix="/miniapp"):
            self.router.get("", self.miniapp_controller.index, name="miniapp.index")
            self.router.post("/validate", self.miniapp_controller.validate, name="miniapp.validate")
            self.router.post("/user", self.miniapp_controller.user_data, name="miniapp.user")
            self.router.post("/send", self.miniapp_controller.send_data, name="miniapp.send")
        
        # Admin routes
        if self.admin_controller:
            with self.router.group(prefix="/admin"):
                self.router.get("", self.admin_controller.index, name="admin.index")
                self.router.get("/login", self.admin_controller.login, name="admin.login")
                self.router.get("/auth", self.admin_controller.authenticate, name="admin.auth")
                self.router.get("/users", self.admin_controller.users, name="admin.users")
                self.router.post("/logout", self.admin_controller.logout, name="admin.logout")
        
        # Применить маршруты к приложению
        self.router.apply_routes(self.app)
    
    def _setup_middlewares(self):
        """Настроить middleware"""
        @web.middleware
        async def cors_middleware(request, handler):
            """CORS middleware"""
            if request.method == "OPTIONS":
                response = web.Response()
            else:
                response = await handler(request)
            
            response.headers['Access-Control-Allow-Origin'] = self.config.web.cors_origins
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            
            return response
        
        self.app.middlewares.append(cors_middleware)
    
    
    async def start(self):
        """Запустить веб-сервер"""
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        site = web.TCPSite(
            self.runner,
            self.config.web.host,
            self.config.web.port
        )
        await site.start()
        
        logger.info(f"Веб-сервер запущен на http://{self.config.web.host}:{self.config.web.port}")
        if self.admin_panel:
            logger.info(f"Админ-панель доступна на http://{self.config.web.host}:{self.config.web.port}/admin")
    
    async def stop(self):
        """Остановить веб-сервер"""
        if self.runner:
            await self.runner.cleanup()
            logger.info("Веб-сервер остановлен")

