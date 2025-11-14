"""
Модуль для работы с SQLite базой данных
"""

import sqlite3
import threading
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager


class Database:
    """Класс для работы с SQLite базой данных с поддержкой потокобезопасности"""
    
    def __init__(self, db_path: str = "bot.db"):
        """
        Инициализация базы данных
        
        Args:
            db_path: Путь к файлу базы данных
        """
        self.db_path = db_path
        self.local = threading.local()
        self._initialize_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получить соединение с базой данных для текущего потока"""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self.local.connection.row_factory = sqlite3.Row
        return self.local.connection
    
    def _initialize_database(self):
        """Инициализация базы данных с созданием стандартных таблиц"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT,
                is_bot INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица состояний пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Таблица чатов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                chat_type TEXT,
                title TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица сообщений
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER,
                chat_id INTEGER,
                user_id INTEGER,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (message_id, chat_id),
                FOREIGN KEY (chat_id) REFERENCES chats (chat_id),
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        # Таблица квизов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                questions TEXT,
                current_question INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        
        conn.commit()
    
    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """
        Выполнить SQL запрос
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            
        Returns:
            Курсор с результатами
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor
    
    def fetchone(self, query: str, params: Tuple = ()) -> Optional[sqlite3.Row]:
        """
        Выполнить запрос и получить одну строку
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            
        Returns:
            Одна строка результата или None
        """
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def fetchall(self, query: str, params: Tuple = ()) -> List[sqlite3.Row]:
        """
        Выполнить запрос и получить все строки
        
        Args:
            query: SQL запрос
            params: Параметры запроса
            
        Returns:
            Список всех строк результата
        """
        cursor = self.execute(query, params)
        return cursor.fetchall()
    
    def add_user(self, user_id: int, username: Optional[str] = None,
                 first_name: Optional[str] = None, last_name: Optional[str] = None,
                 language_code: Optional[str] = None, is_bot: bool = False):
        """Добавить или обновить пользователя"""
        self.execute("""
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, language_code, is_bot, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, username, first_name, last_name, language_code, int(is_bot)))
    
    def get_user(self, user_id: int) -> Optional[sqlite3.Row]:
        """Получить информацию о пользователе"""
        return self.fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
    
    def set_user_state(self, user_id: int, state: str, data: Optional[str] = None):
        """Установить состояние пользователя"""
        self.execute("""
            INSERT OR REPLACE INTO user_states (user_id, state, data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, state, data))
    
    def get_user_state(self, user_id: int) -> Optional[sqlite3.Row]:
        """Получить состояние пользователя"""
        return self.fetchone("SELECT * FROM user_states WHERE user_id = ?", (user_id,))
    
    def clear_user_state(self, user_id: int):
        """Очистить состояние пользователя"""
        self.execute("DELETE FROM user_states WHERE user_id = ?", (user_id,))
    
    def add_chat(self, chat_id: int, chat_type: str, title: Optional[str] = None,
                 username: Optional[str] = None):
        """Добавить или обновить чат"""
        self.execute("""
            INSERT OR REPLACE INTO chats (chat_id, chat_type, title, username, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (chat_id, chat_type, title, username))
    
    def save_message(self, message_id: int, chat_id: int, user_id: int, text: Optional[str]):
        """Сохранить сообщение"""
        self.execute("""
            INSERT OR REPLACE INTO messages (message_id, chat_id, user_id, text)
            VALUES (?, ?, ?, ?)
        """, (message_id, chat_id, user_id, text))
    
    def close(self):
        """Закрыть соединение с базой данных"""
        if hasattr(self.local, 'connection'):
            self.local.connection.close()
            delattr(self.local, 'connection')

