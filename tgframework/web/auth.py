"""
Авторизация через Telegram
"""

import hashlib
import hmac
import time
from typing import Optional, Dict
from urllib.parse import parse_qs


class TelegramAuth:
    """Авторизация через Telegram Widget"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.secret_key = hashlib.sha256(bot_token.encode()).digest()
    
    def verify_telegram_auth(self, auth_data: Dict) -> bool:
        """
        Проверить данные авторизации от Telegram
        
        Args:
            auth_data: Данные от Telegram Widget
            
        Returns:
            True если данные валидны
        """
        if 'hash' not in auth_data:
            return False
        
        received_hash = auth_data.pop('hash')
        
        # Проверка времени (данные не старше 1 дня)
        auth_date = int(auth_data.get('auth_date', 0))
        if time.time() - auth_date > 86400:
            return False
        
        # Создание строки для проверки
        data_check_string = '\n'.join([f'{k}={v}' for k, v in sorted(auth_data.items())])
        
        # Вычисление hash
        computed_hash = hmac.new(
            self.secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return computed_hash == received_hash
    
    def parse_auth_data(self, query_string: str) -> Optional[Dict]:
        """
        Распарсить данные авторизации из query string
        
        Args:
            query_string: Query string от Telegram
            
        Returns:
            Словарь с данными пользователя или None
        """
        try:
            auth_data = {}
            for key, value in parse_qs(query_string).items():
                auth_data[key] = value[0] if value else ''
            
            if self.verify_telegram_auth(auth_data):
                return {
                    'id': int(auth_data.get('id', 0)),
                    'first_name': auth_data.get('first_name'),
                    'last_name': auth_data.get('last_name'),
                    'username': auth_data.get('username'),
                    'photo_url': auth_data.get('photo_url'),
                    'auth_date': int(auth_data.get('auth_date', 0)),
                }
            
            return None
        except Exception:
            return None

