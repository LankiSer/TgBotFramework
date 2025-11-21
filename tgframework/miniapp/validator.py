"""
Валидация данных Mini App
"""

import hashlib
import hmac
from typing import Dict, Optional
from urllib.parse import parse_qs, unquote


class MiniAppValidator:
    """Валидатор данных от Telegram Mini App"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
    
    def validate_init_data(self, init_data: str) -> Optional[Dict]:
        """
        Проверить данные от Mini App
        
        Args:
            init_data: Строка initData от Telegram.WebApp
            
        Returns:
            Распарсенные данные или None если невалидно
        """
        try:
            # Парсим данные
            parsed_data = {}
            for item in init_data.split('&'):
                if '=' in item:
                    key, value = item.split('=', 1)
                    parsed_data[key] = unquote(value)
            
            if 'hash' not in parsed_data:
                return None
            
            received_hash = parsed_data.pop('hash')
            
            # Создаем data-check-string
            data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
            data_check_string = '\n'.join(data_check_arr)
            
            # Создаем secret key
            secret_key = hmac.new(
                b"WebAppData",
                self.bot_token.encode(),
                hashlib.sha256
            ).digest()
            
            # Вычисляем hash
            computed_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if computed_hash != received_hash:
                return None
            
            return parsed_data
            
        except Exception:
            return None
    
    def validate_webapp_data(self, init_data: str) -> bool:
        """
        Проверить валидность данных
        
        Args:
            init_data: Строка initData
            
        Returns:
            True если данные валидны
        """
        return self.validate_init_data(init_data) is not None

