# -*- coding: utf-8 -*-
"""
React SSR (Server-Side Rendering) renderer
Передает серверные данные в React приложение
"""

import os
import json
from typing import Dict, Any, Optional
from aiohttp import web


class ReactRenderer:
    """
    Рендерер для React приложений с server-side props
    
    Использование:
        renderer = ReactRenderer('/path/to/build')
        props = {'user': {...}, 'page': 'home'}
        return renderer.render(props)
    """
    
    def __init__(self, build_dir: str, title: str = "My Bot"):
        """
        Args:
            build_dir: Путь к собранному React приложению
            title: Заголовок страницы
        """
        self.build_dir = build_dir
        self.title = title
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Загружает manifest.json из build"""
        manifest_path = os.path.join(self.build_dir, 'manifest.json')
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def render(
        self, 
        props: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None
    ) -> web.Response:
        """
        Рендерит React приложение с server-side props
        
        Args:
            props: Данные для передачи в React (user, stats, и т.д.)
            title: Заголовок страницы (опционально)
            
        Returns:
            aiohttp Response с HTML
            
        Example:
            props = {
                'user': {
                    'user_id': 123,
                    'first_name': 'John',
                    'photo_url': 'https://...'
                },
                'page': 'profile'
            }
            return renderer.render(props)
        """
        if props is None:
            props = {}
        
        page_title = title or self.title
        
        # Получаем пути к JS и CSS из manifest
        main_js = self.manifest.get('main.tsx', {}).get('file', 'assets/main.js')
        main_css = self.manifest.get('main.tsx', {}).get('css', [])
        
        # Генерируем HTML
        css_tags = ''.join(
            f'<link rel="stylesheet" href="/static/dist/{css}">\n    '
            for css in main_css
        )
        
        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    {css_tags}
    <script>
        window.__SERVER_PROPS__ = {json.dumps(props, ensure_ascii=False)};
    </script>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/static/dist/{main_js}"></script>
</body>
</html>"""
        
        return web.Response(
            text=html,
            content_type='text/html',
            charset='utf-8'
        )
    
    def json_response(self, data: Dict[str, Any], status: int = 200) -> web.Response:
        """
        Возвращает JSON ответ
        
        Args:
            data: Данные для JSON
            status: HTTP статус
            
        Returns:
            JSON Response
        """
        return web.json_response(
            data,
            status=status,
            dumps=lambda obj: json.dumps(obj, ensure_ascii=False)
        )


def get_telegram_user_photo_url(bot_token: str, user_id: int) -> Optional[str]:
    """
    Получает URL аватарки пользователя из Telegram
    
    Args:
        bot_token: Токен бота
        user_id: ID пользователя
        
    Returns:
        URL фото или None
        
    Example:
        photo_url = get_telegram_user_photo_url(config.bot.token, 123456)
    """
    import aiohttp
    import asyncio
    
    async def fetch_photo():
        url = f"https://api.telegram.org/bot{bot_token}/getUserProfilePhotos"
        params = {"user_id": user_id, "limit": 1}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("ok") and data.get("result", {}).get("photos"):
                            file_id = data["result"]["photos"][0][0]["file_id"]
                            
                            # Получаем путь к файлу
                            file_url = f"https://api.telegram.org/bot{bot_token}/getFile"
                            async with session.get(file_url, params={"file_id": file_id}, timeout=aiohttp.ClientTimeout(total=5)) as file_response:
                                if file_response.status == 200:
                                    file_data = await file_response.json()
                                    if file_data.get("ok"):
                                        file_path = file_data["result"]["file_path"]
                                        return f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
        except:
            pass
        return None
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если цикл уже работает, создаем задачу
            return None
        return loop.run_until_complete(fetch_photo())
    except:
        return None

