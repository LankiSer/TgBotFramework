"""
Система миграций
"""

from typing import List, Type
from .models import Model
from .engine import DatabaseEngine
import logging

logger = logging.getLogger(__name__)


class Migration:
    """Базовый класс миграции"""
    
    def up(self, engine: DatabaseEngine):
        """Применить миграцию"""
        raise NotImplementedError
    
    def down(self, engine: DatabaseEngine):
        """Откатить миграцию"""
        raise NotImplementedError


class MigrationManager:
    """Менеджер миграций"""
    
    def __init__(self, engine: DatabaseEngine):
        self.engine = engine
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Создать таблицу миграций если её нет"""
        self.engine.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.engine.commit()
    
    def is_applied(self, migration_name: str) -> bool:
        """Проверить, применена ли миграция"""
        row = self.engine.fetchone(
            "SELECT * FROM migrations WHERE name = ?",
            (migration_name,)
        )
        return row is not None
    
    def apply(self, migration: Migration, name: str):
        """Применить миграцию"""
        if self.is_applied(name):
            logger.info(f"Миграция {name} уже применена")
            return
        
        logger.info(f"Применение миграции {name}...")
        migration.up(self.engine)
        
        self.engine.execute(
            "INSERT INTO migrations (name) VALUES (?)",
            (name,)
        )
        self.engine.commit()
        logger.info(f"Миграция {name} применена")
    
    def rollback(self, migration: Migration, name: str):
        """Откатить миграцию"""
        if not self.is_applied(name):
            logger.info(f"Миграция {name} не применена")
            return
        
        logger.info(f"Откат миграции {name}...")
        migration.down(self.engine)
        
        self.engine.execute(
            "DELETE FROM migrations WHERE name = ?",
            (name,)
        )
        self.engine.commit()
        logger.info(f"Миграция {name} откачена")
    
    def create_table_from_model(self, model: Type[Model]):
        """Создать таблицу из модели"""
        table_name = model.get_table_name()
        fields = model.get_fields()
        
        # Определяем тип движка
        engine_type = "sqlite" if "sqlite" in self.engine.connection_string else "postgresql"
        
        columns = []
        for field_name, field in fields.items():
            sql_type = field.get_sql_type(engine_type)
            column_def = f"{field_name} {sql_type}"
            
            if field.primary_key:
                if engine_type == "sqlite":
                    column_def += " PRIMARY KEY"
                    if hasattr(field, 'auto_increment') and field.auto_increment:
                        column_def += " AUTOINCREMENT"
                else:  # postgresql
                    column_def += " PRIMARY KEY"
            
            if not field.nullable and not field.primary_key:
                column_def += " NOT NULL"
            
            if field.unique and not field.primary_key:
                column_def += " UNIQUE"
            
            if field.default is not None and not hasattr(field, 'auto_increment'):
                if isinstance(field.default, str):
                    column_def += f" DEFAULT '{field.default}'"
                else:
                    column_def += f" DEFAULT {field.default}"
            
            columns.append(column_def)
        
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        logger.info(f"Создание таблицы: {query}")
        self.engine.execute(query)
        self.engine.commit()
        logger.info(f"Таблица {table_name} создана")

