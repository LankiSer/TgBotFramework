"""
Контроллер для Telegram Mini Apps
"""

from aiohttp import web
from ..routing import Controller
from ...miniapp import MiniAppValidator, ReactRenderer


class MiniAppController(Controller):
    """Контроллер для Mini Apps"""
    
    def __init__(self, config=None, session=None):
        super().__init__()
        self.config = config
        self.session = session
        self.validator = MiniAppValidator(config.bot.token) if config else None
        self.renderer = ReactRenderer()
    
    async def index(self, request: web.Request):
        """GET /miniapp - главная страница Mini App"""
        # Серверные данные для передачи в React
        context = {
            "app_name": "TgFramework Mini App",
            "api_url": f"http://{self.config.web.host}:{self.config.web.port}/api" if self.config else "/api",
            "features": [
                "Real-time updates",
                "Telegram authentication",
                "Server-side rendering"
            ]
        }
        
        html = self.renderer.render("miniapp.html", context)
        return web.Response(text=html, content_type="text/html")
    
    async def validate(self, request: web.Request):
        """POST /miniapp/validate - валидация данных Mini App"""
        if not self.validator:
            return self.error("Validator not configured", 500)
        
        try:
            data = await request.json()
            init_data = data.get("initData")
            
            if not init_data:
                return self.error("initData is required", 400)
            
            validated = self.validator.validate_init_data(init_data)
            
            if not validated:
                return self.error("Invalid initData", 403)
            
            return self.success(validated, "Data validated successfully")
        except Exception as e:
            return self.error(str(e), 500)
    
    async def user_data(self, request: web.Request):
        """POST /miniapp/user - получить данные пользователя Mini App"""
        if not self.validator or not self.session:
            return self.error("Service not configured", 500)
        
        try:
            data = await request.json()
            init_data = data.get("initData")
            
            if not init_data:
                return self.error("initData is required", 400)
            
            validated = self.validator.validate_init_data(init_data)
            
            if not validated:
                return self.error("Invalid initData", 403)
            
            # Получаем данные пользователя из БД
            user_id = validated.get("user", {}).get("id")
            if user_id:
                from ...domain import UserService, UserRepository
                
                user_service = UserService(UserRepository(self.session))
                user = user_service.get_user(int(user_id))
                
                if user:
                    return self.success({
                        "user_id": user.user_id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "full_name": user.full_name,
                        "is_admin": user.is_admin,
                    })
            
            return self.error("User not found", 404)
        except Exception as e:
            return self.error(str(e), 500)
    
    async def send_data(self, request: web.Request):
        """POST /miniapp/send - отправить данные из Mini App в бота"""
        if not self.validator:
            return self.error("Service not configured", 500)
        
        try:
            data = await request.json()
            init_data = data.get("initData")
            payload = data.get("payload")
            
            if not init_data or not payload:
                return self.error("initData and payload are required", 400)
            
            validated = self.validator.validate_init_data(init_data)
            
            if not validated:
                return self.error("Invalid initData", 403)
            
            # Здесь можно обработать данные от Mini App
            # Например, сохранить в БД или отправить в бота
            
            return self.success({
                "received": payload,
                "user_id": validated.get("user", {}).get("id")
            }, "Data received successfully")
        except Exception as e:
            return self.error(str(e), 500)

