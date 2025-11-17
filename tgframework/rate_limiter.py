"""
Rate limiter для защиты от превышения лимитов Telegram API
"""

import time
from typing import Dict, Optional
from collections import defaultdict
import asyncio


class RateLimiter:
    """Rate limiter с поддержкой различных стратегий"""
    
    def __init__(self, max_calls: int = 30, period: float = 1.0):
        """
        Инициализация rate limiter
        
        Args:
            max_calls: Максимальное количество вызовов
            period: Период в секундах
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: Dict[str, list] = defaultdict(list)
        self.lock = asyncio.Lock()
    
    async def acquire(self, key: str = "default") -> bool:
        """
        Попытаться получить разрешение на выполнение
        
        Args:
            key: Ключ для группировки вызовов
            
        Returns:
            True если разрешено, False если нужно подождать
        """
        async with self.lock:
            now = time.time()
            # Удаляем старые вызовы
            self.calls[key] = [call_time for call_time in self.calls[key] 
                             if now - call_time < self.period]
            
            if len(self.calls[key]) < self.max_calls:
                self.calls[key].append(now)
                return True
            return False
    
    async def wait(self, key: str = "default"):
        """Подождать пока не будет доступен слот"""
        while not await self.acquire(key):
            await asyncio.sleep(0.1)


class TelegramRateLimiter:
    """Rate limiter специально для Telegram API"""
    
    def __init__(self):
        # Telegram API лимиты:
        # - 30 сообщений в секунду для групп
        # - 20 сообщений в минуту для одного пользователя
        self.global_limiter = RateLimiter(max_calls=30, period=1.0)
        self.user_limiter = RateLimiter(max_calls=20, period=60.0)
    
    async def wait_message(self, user_id: Optional[int] = None):
        """Подождать перед отправкой сообщения"""
        await self.global_limiter.wait()
        if user_id:
            await self.user_limiter.wait(str(user_id))

