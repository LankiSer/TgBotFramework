"""
Контроллер админ-панели
"""

import base64
import json
from aiohttp import web
from ..routing import Controller
from ..auth import TelegramAuth


class AdminController(Controller):
    """Контроллер админ-панели"""
    
    def __init__(self, session=None, auth: TelegramAuth = None):
        super().__init__()
        self.session = session
        self.auth = auth
    
    def _check_admin(self, request: web.Request) -> bool:
        """Проверить права администратора"""
        session_cookie = request.cookies.get('admin_session')
        if not session_cookie:
            return False
        
        try:
            session_data = json.loads(base64.b64decode(session_cookie).decode())
            user_id = session_data.get('user_id')
            
            if not user_id or not self.session:
                return False
            
            from ...domain import UserService, UserRepository
            user_service = UserService(UserRepository(self.session))
            return user_service.is_admin(user_id)
        except Exception:
            return False
    
    async def index(self, request: web.Request):
        """GET /admin - главная страница админки"""
        if not self._check_admin(request):
            return self.redirect("/admin/login")
        
        html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Админ-панель</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 { color: #333; margin-bottom: 30px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            color: white;
            text-align: center;
        }
        .stat-card h3 { font-size: 14px; opacity: 0.9; margin-bottom: 10px; }
        .stat-card p { font-size: 36px; font-weight: bold; }
        .menu {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        .menu-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            color: #333;
            display: block;
        }
        .menu-item:hover {
            background: #667eea;
            color: white;
            transform: translateY(-5px);
        }
        .logout-btn {
            background: #dc3545;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 20px;
            width: 100%;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Админ-панель</h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Всего пользователей</h3>
                <p id="user-count">-</p>
            </div>
            <div class="stat-card">
                <h3>Администраторов</h3>
                <p id="admin-count">-</p>
            </div>
        </div>
        
        <div class="menu">
            <a href="/admin/users" class="menu-item">Пользователи</a>
            <a href="/admin/stats" class="menu-item">Статистика</a>
            <a href="/api" class="menu-item">API</a>
            <a href="/miniapp" class="menu-item">Mini App</a>
        </div>
        
        <button class="logout-btn" onclick="logout()">Выйти</button>
    </div>
    
    <script>
        async function loadStats() {
            const response = await fetch('/api/stats');
            const result = await response.json();
            if (result.success) {
                document.getElementById('user-count').textContent = result.data.total_users;
                document.getElementById('admin-count').textContent = result.data.total_admins;
            }
        }
        
        async function logout() {
            await fetch('/admin/logout', { method: 'POST' });
            window.location.href = '/admin/login';
        }
        
        loadStats();
    </script>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def login(self, request: web.Request):
        """GET /admin/login - страница входа"""
        bot_token = self.auth.bot_token.split(':')[0] if self.auth else ""
        
        html = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Вход в админ-панель</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }}
        .login-container {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 60px 40px;
            text-align: center;
            max-width: 400px;
            width: 100%;
        }}
        h1 {{ color: #333; margin-bottom: 20px; font-size: 32px; }}
        p {{ color: #666; margin-bottom: 40px; font-size: 16px; }}
    </style>
    <script async src="https://telegram.org/js/telegram-widget.js?22" 
            data-telegram-login="{bot_token}" 
            data-size="large" 
            data-auth-url="/admin/auth" 
            data-request-access="write">
    </script>
</head>
<body>
    <div class="login-container">
        <h1>Вход в админ-панель</h1>
        <p>Войдите через Telegram для доступа к админ-панели</p>
    </div>
</body>
</html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def authenticate(self, request: web.Request):
        """GET /admin/auth - обработка авторизации"""
        if not self.auth or not self.session:
            return self.redirect("/admin/login?error=config")
        
        query_string = request.query_string
        user_data = self.auth.parse_auth_data(query_string)
        
        if not user_data:
            return self.redirect('/admin/login?error=invalid')
        
        user_id = user_data['id']
        
        from ...domain import UserService, UserRepository
        user_service = UserService(UserRepository(self.session))
        
        if not user_service.is_admin(user_id):
            return self.redirect('/admin/login?error=not_admin')
        
        session_data = {
            'user_id': user_id,
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
        }
        
        session_cookie = base64.b64encode(json.dumps(session_data).encode()).decode()
        
        response = web.HTTPFound('/admin')
        response.set_cookie('admin_session', session_cookie, max_age=86400, httponly=True)
        
        return response
    
    async def logout(self, request: web.Request):
        """POST /admin/logout - выход"""
        response = self.json({"success": True})
        response.del_cookie('admin_session')
        return response
    
    async def users(self, request: web.Request):
        """GET /admin/users - список пользователей"""
        if not self._check_admin(request):
            return self.error("Unauthorized", 401)
        
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
                    "is_admin": u.is_admin,
                }
                for u in users
            ])
        except Exception as e:
            return self.error(str(e), 500)

