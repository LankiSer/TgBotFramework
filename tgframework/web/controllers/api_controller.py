"""
API контроллер для работы с данными
"""

from aiohttp import web
from ..routing import Controller


class ApiController(Controller):
    """Контроллер для API endpoints"""
    
    def __init__(self, session=None, bot=None):
        super().__init__()
        self.session = session
        self.bot = bot
    
    async def index(self, request: web.Request):
        """GET /api - информация об API"""
        return self.json({
            "name": "TgFramework API",
            "version": "3.0.0",
            "endpoints": {
                "users": "/api/users",
                "stats": "/api/stats",
                "miniapp": "/api/miniapp",
            }
        })
    
    async def users(self, request: web.Request):
        """GET /api/users - список пользователей"""
        if not self.session:
            return self.error("Database not configured", 500)
        
        try:
            from ...domain import UserService, UserRepository
            
            user_service = UserService(UserRepository(self.session))
            users = user_service.get_all_users(limit=100)
            
            return self.success([
                {
                    "user_id": u.user_id,
                    "username": u.username,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "is_admin": u.is_admin,
                }
                for u in users
            ])
        except Exception as e:
            return self.error(str(e), 500)
    
    async def user_detail(self, request: web.Request, id: str):
        """GET /api/users/{id} - информация о пользователе"""
        if not self.session:
            return self.error("Database not configured", 500)
        
        try:
            from ...domain import UserService, UserRepository
            
            user_service = UserService(UserRepository(self.session))
            user = user_service.get_user(int(id))
            
            if not user:
                return self.error("User not found", 404)
            
            return self.success({
                "user_id": user.user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "is_admin": user.is_admin,
                "is_bot": user.is_bot,
            })
        except Exception as e:
            return self.error(str(e), 500)
    
    async def stats(self, request: web.Request):
        """GET /api/stats - статистика бота"""
        if not self.session:
            return self.error("Database not configured", 500)
        
        try:
            from ...domain import UserService, UserRepository
            
            user_service = UserService(UserRepository(self.session))
            
            return self.success({
                "total_users": user_service.get_user_count(),
                "total_admins": len(user_service.get_admins()),
            })
        except Exception as e:
            return self.error(str(e), 500)
    
    async def send_message(self, request: web.Request):
        """POST /api/send - отправить сообщение"""
        if not self.bot:
            return self.error("Bot not configured", 500)
        
        try:
            data = await request.json()
            chat_id = data.get("chat_id")
            text = data.get("text")
            
            if not chat_id or not text:
                return self.error("chat_id and text are required", 400)
            
            result = await self.bot.send_message(chat_id, text)
            
            return self.success(result, "Message sent successfully")
        except Exception as e:
            return self.error(str(e), 500)

