"""
Шаблоны для создания дефолтных миграций
"""

from pathlib import Path
from datetime import datetime


def create_default_migrations(migrations_path: Path):
    """
    Создать дефолтные миграции для базовых таблиц
    
    Args:
        migrations_path: Путь к директории миграций
    """
    migrations_path.mkdir(exist_ok=True)
    
    # 1. Миграция для таблицы users
    create_users_migration(migrations_path)
    
    # 2. Миграция для таблицы chats
    create_chats_migration(migrations_path)
    
    # 3. Миграция для таблицы messages
    create_messages_migration(migrations_path)
    
    # 4. Миграция для таблицы user_states
    create_user_states_migration(migrations_path)
    
    # __init__.py
    (migrations_path / "__init__.py").write_text('"""Migrations"""\n')


def create_users_migration(migrations_path: Path):
    """Создать миграцию для таблицы users"""
    timestamp = "2024_01_01_000001"
    content = '''"""
Create users table
"""

from tgframework.orm import Migration, DatabaseEngine


class CreateUsersTable(Migration):
    """Create users table migration"""
    
    def up(self, engine: DatabaseEngine):
        """Apply migration"""
        is_postgres = "postgresql" in engine.connection_string
        
        query = """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT,
                is_bot INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        if is_postgres:
            query = query.replace("INTEGER DEFAULT 0", "BOOLEAN DEFAULT FALSE")
            query = query.replace("INTEGER PRIMARY KEY", "BIGINT PRIMARY KEY")
        
        engine.execute(query)
        engine.commit()
    
    def down(self, engine: DatabaseEngine):
        """Rollback migration"""
        engine.execute("DROP TABLE IF EXISTS users")
        engine.commit()
'''
    
    (migrations_path / f"{timestamp}_create_users_table.py").write_text(content)


def create_chats_migration(migrations_path: Path):
    """Создать миграцию для таблицы chats"""
    timestamp = "2024_01_01_000002"
    content = '''"""
Create chats table
"""

from tgframework.orm import Migration, DatabaseEngine


class CreateChatsTable(Migration):
    """Create chats table migration"""
    
    def up(self, engine: DatabaseEngine):
        """Apply migration"""
        is_postgres = "postgresql" in engine.connection_string
        
        query = """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id INTEGER PRIMARY KEY,
                chat_type TEXT NOT NULL,
                title TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        if is_postgres:
            query = query.replace("INTEGER PRIMARY KEY", "BIGINT PRIMARY KEY")
            query = query.replace("TEXT", "VARCHAR(255)")
        
        engine.execute(query)
        engine.commit()
    
    def down(self, engine: DatabaseEngine):
        """Rollback migration"""
        engine.execute("DROP TABLE IF EXISTS chats")
        engine.commit()
'''
    
    (migrations_path / f"{timestamp}_create_chats_table.py").write_text(content)


def create_messages_migration(migrations_path: Path):
    """Создать миграцию для таблицы messages"""
    timestamp = "2024_01_01_000003"
    content = '''"""
Create messages table
"""

from tgframework.orm import Migration, DatabaseEngine


class CreateMessagesTable(Migration):
    """Create messages table migration"""
    
    def up(self, engine: DatabaseEngine):
        """Apply migration"""
        is_postgres = "postgresql" in engine.connection_string
        
        query = """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        if is_postgres:
            query = query.replace("AUTOINCREMENT", "")
            query = query.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
            query = query.replace("INTEGER NOT NULL", "BIGINT NOT NULL")
        
        engine.execute(query)
        
        # Создаём индексы
        engine.execute("CREATE INDEX IF NOT EXISTS idx_messages_chat_id ON messages(chat_id)")
        engine.execute("CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id)")
        
        engine.commit()
    
    def down(self, engine: DatabaseEngine):
        """Rollback migration"""
        engine.execute("DROP TABLE IF EXISTS messages")
        engine.commit()
'''
    
    (migrations_path / f"{timestamp}_create_messages_table.py").write_text(content)


def create_user_states_migration(migrations_path: Path):
    """Создать миграцию для таблицы user_states"""
    timestamp = "2024_01_01_000004"
    content = '''"""
Create user_states table
"""

from tgframework.orm import Migration, DatabaseEngine


class CreateUserStatesTable(Migration):
    """Create user_states table migration"""
    
    def up(self, engine: DatabaseEngine):
        """Apply migration"""
        is_postgres = "postgresql" in engine.connection_string
        
        query = """
            CREATE TABLE IF NOT EXISTS user_states (
                user_id INTEGER PRIMARY KEY,
                state TEXT,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        if is_postgres:
            query = query.replace("INTEGER PRIMARY KEY", "BIGINT PRIMARY KEY")
            query = query.replace("TEXT", "VARCHAR(255)")
            query = query.replace("data VARCHAR(255)", "data TEXT")
        
        engine.execute(query)
        engine.commit()
    
    def down(self, engine: DatabaseEngine):
        """Rollback migration"""
        engine.execute("DROP TABLE IF EXISTS user_states")
        engine.commit()
'''
    
    (migrations_path / f"{timestamp}_create_user_states_table.py").write_text(content)

