"""
Движок базы данных с поддержкой SQLite и PostgreSQL
"""

import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Literal
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DatabaseEngine(ABC):
    """Абстрактный класс для работы с БД"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    @abstractmethod
    def connect(self):
        """Подключиться к БД"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Отключиться от БД"""
        pass
    
    @abstractmethod
    def execute(self, query: str, params: Tuple = ()) -> Any:
        """Выполнить запрос"""
        pass
    
    @abstractmethod
    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Получить одну строку"""
        pass
    
    @abstractmethod
    def fetchall(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Получить все строки"""
        pass
    
    @abstractmethod
    def commit(self):
        """Зафиксировать транзакцию"""
        pass
    
    @abstractmethod
    def rollback(self):
        """Откатить транзакцию"""
        pass


class SQLiteEngine(DatabaseEngine):
    """Движок для SQLite"""
    
    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        self.db_path = connection_string.replace("sqlite:///", "")
    
    def connect(self):
        """Подключиться к SQLite"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        logger.info(f"Подключено к SQLite: {self.db_path}")
    
    def disconnect(self):
        """Отключиться от SQLite"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Отключено от SQLite")
    
    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """Выполнить запрос"""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        logger.debug(f"Executing: {query} with params {params}")
        cursor.execute(query, params)
        return cursor
    
    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Получить одну строку"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def fetchall(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Получить все строки"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def commit(self):
        """Зафиксировать транзакцию"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Откатить транзакцию"""
        if self.connection:
            self.connection.rollback()
    
    def get_placeholder(self) -> str:
        """Получить placeholder для параметров"""
        return "?"


class PostgreSQLEngine(DatabaseEngine):
    """Движок для PostgreSQL"""
    
    def __init__(self, connection_string: str):
        super().__init__(connection_string)
        try:
            import psycopg2
            import psycopg2.extras
            self.psycopg2 = psycopg2
            self.extras = psycopg2.extras
        except ImportError:
            raise ImportError("psycopg2 не установлен. Установите: pip install psycopg2-binary")
    
    def connect(self):
        """Подключиться к PostgreSQL"""
        # Парсим connection string
        # postgresql://user:password@host:port/database
        parts = self.connection_string.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_port_db = parts[1].split("/")
        host_port = host_port_db[0].split(":")
        
        self.connection = self.psycopg2.connect(
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database=host_port_db[1],
            user=user_pass[0],
            password=user_pass[1] if len(user_pass) > 1 else "",
            cursor_factory=self.extras.RealDictCursor
        )
        logger.info(f"Подключено к PostgreSQL: {host_port[0]}:{host_port[1] if len(host_port) > 1 else 5432}")
    
    def disconnect(self):
        """Отключиться от PostgreSQL"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Отключено от PostgreSQL")
    
    def execute(self, query: str, params: Tuple = ()) -> Any:
        """Выполнить запрос"""
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        # PostgreSQL использует %s вместо ?
        query = query.replace("?", "%s")
        logger.debug(f"Executing: {query} with params {params}")
        cursor.execute(query, params)
        return cursor
    
    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """Получить одну строку"""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def fetchall(self, query: str, params: Tuple = ()) -> List[Dict]:
        """Получить все строки"""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def commit(self):
        """Зафиксировать транзакцию"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Откатить транзакцию"""
        if self.connection:
            self.connection.rollback()
    
    def get_placeholder(self) -> str:
        """Получить placeholder для параметров"""
        return "%s"


def create_engine(connection_string: str) -> DatabaseEngine:
    """
    Создать движок БД на основе строки подключения
    
    Args:
        connection_string: Строка подключения (sqlite:/// или postgresql://)
        
    Returns:
        Экземпляр DatabaseEngine
    """
    if connection_string.startswith("sqlite://"):
        return SQLiteEngine(connection_string)
    elif connection_string.startswith("postgresql://"):
        return PostgreSQLEngine(connection_string)
    else:
        raise ValueError(f"Неподдерживаемый движок БД: {connection_string}")

