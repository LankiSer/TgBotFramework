"""
Система миграций в стиле Laravel
"""

import os
import importlib.util
from typing import List, Type, Optional
from pathlib import Path
from datetime import datetime
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
    """Менеджер миграций в стиле Laravel"""
    
    def __init__(self, engine: DatabaseEngine, migrations_path: str = "migrations"):
        self.engine = engine
        self.migrations_path = Path(migrations_path)
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Создать таблицу миграций"""
        query = """
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration TEXT NOT NULL UNIQUE,
                batch INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        # Адаптируем для PostgreSQL
        if "postgresql" in self.engine.connection_string:
            query = query.replace("AUTOINCREMENT", "")
            query = query.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
        
        self.engine.execute(query)
        self.engine.commit()
    
    def is_applied(self, migration_name: str) -> bool:
        """Проверить, применена ли миграция"""
        row = self.engine.fetchone(
            "SELECT * FROM migrations WHERE migration = ?",
            (migration_name,)
        )
        return row is not None
    
    def get_applied_migrations(self) -> List[str]:
        """Получить список примененных миграций"""
        rows = self.engine.fetchall(
            "SELECT migration FROM migrations ORDER BY id"
        )
        return [row["migration"] for row in rows]
    
    def get_pending_migrations(self) -> List[str]:
        """Получить список неприменённых миграций"""
        all_migrations = self._get_migration_files()
        applied = self.get_applied_migrations()
        return [m for m in all_migrations if m not in applied]
    
    def get_last_batch(self) -> int:
        """Получить номер последнего батча"""
        row = self.engine.fetchone("SELECT MAX(batch) as batch FROM migrations")
        return row["batch"] if row and row["batch"] else 0
    
    def _get_migration_files(self) -> List[str]:
        """Получить список файлов миграций"""
        if not self.migrations_path.exists():
            return []
        
        migrations = []
        for file in sorted(self.migrations_path.glob("*.py")):
            if file.name != "__init__.py":
                migrations.append(file.stem)
        
        return migrations
    
    def _load_migration(self, migration_name: str) -> Optional[Migration]:
        """Загрузить миграцию из файла"""
        migration_file = self.migrations_path / f"{migration_name}.py"
        
        if not migration_file.exists():
            logger.error(f"Migration file not found: {migration_file}")
            return None
        
        # Загружаем модуль
        spec = importlib.util.spec_from_file_location(migration_name, migration_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Ищем класс миграции
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, Migration) and attr is not Migration:
                return attr()
        
        logger.error(f"No Migration class found in {migration_file}")
        return None
    
    def migrate(self, steps: Optional[int] = None):
        """
        Применить миграции (как php artisan migrate)
        
        Args:
            steps: Количество миграций для применения (None = все)
        """
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("Nothing to migrate")
            return
        
        if steps:
            pending = pending[:steps]
        
        batch = self.get_last_batch() + 1
        
        for migration_name in pending:
            logger.info(f"Migrating: {migration_name}")
            
            migration = self._load_migration(migration_name)
            if not migration:
                continue
            
            try:
                migration.up(self.engine)
                
                self.engine.execute(
                    "INSERT INTO migrations (migration, batch) VALUES (?, ?)",
                    (migration_name, batch)
                )
                self.engine.commit()
                
                logger.info(f"Migrated: {migration_name}")
            except Exception as e:
                logger.error(f"Error migrating {migration_name}: {e}")
                self.engine.rollback()
                raise
    
    def rollback(self, steps: int = 1):
        """
        Откатить последний батч миграций (как php artisan migrate:rollback)
        
        Args:
            steps: Количество батчей для отката
        """
        last_batch = self.get_last_batch()
        
        if last_batch == 0:
            logger.info("Nothing to rollback")
            return
        
        target_batch = max(0, last_batch - steps + 1)
        
        # Получаем миграции для отката
        rows = self.engine.fetchall(
            "SELECT migration FROM migrations WHERE batch >= ? ORDER BY id DESC",
            (target_batch,)
        )
        
        if not rows:
            logger.info("Nothing to rollback")
            return
        
        for row in rows:
            migration_name = row["migration"]
            logger.info(f"Rolling back: {migration_name}")
            
            migration = self._load_migration(migration_name)
            if not migration:
                continue
            
            try:
                migration.down(self.engine)
                
                self.engine.execute(
                    "DELETE FROM migrations WHERE migration = ?",
                    (migration_name,)
                )
                self.engine.commit()
                
                logger.info(f"Rolled back: {migration_name}")
            except Exception as e:
                logger.error(f"Error rolling back {migration_name}: {e}")
                self.engine.rollback()
                raise
    
    def reset(self):
        """Откатить все миграции (как php artisan migrate:reset)"""
        applied = self.get_applied_migrations()
        
        if not applied:
            logger.info("Nothing to reset")
            return
        
        # Откатываем в обратном порядке
        for migration_name in reversed(applied):
            logger.info(f"Rolling back: {migration_name}")
            
            migration = self._load_migration(migration_name)
            if not migration:
                continue
            
            try:
                migration.down(self.engine)
                
                self.engine.execute(
                    "DELETE FROM migrations WHERE migration = ?",
                    (migration_name,)
                )
                self.engine.commit()
                
                logger.info(f"Rolled back: {migration_name}")
            except Exception as e:
                logger.error(f"Error rolling back {migration_name}: {e}")
                self.engine.rollback()
                raise
    
    def refresh(self):
        """Откатить и применить заново все миграции (как php artisan migrate:refresh)"""
        logger.info("Refreshing database...")
        self.reset()
        self.migrate()
        logger.info("Database refreshed")
    
    def fresh(self):
        """Удалить все таблицы и применить миграции заново (как php artisan migrate:fresh)"""
        logger.info("Dropping all tables...")
        
        # Получаем список таблиц
        if "sqlite" in self.engine.connection_string:
            rows = self.engine.fetchall(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        else:  # PostgreSQL
            rows = self.engine.fetchall(
                "SELECT tablename as name FROM pg_tables WHERE schemaname='public'"
            )
        
        # Удаляем таблицы
        for row in rows:
            table_name = row["name"]
            logger.info(f"Dropping table: {table_name}")
            self.engine.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        
        self.engine.commit()
        
        # Пересоздаём таблицу миграций
        self._ensure_migrations_table()
        
        # Применяем миграции
        logger.info("Running migrations...")
        self.migrate()
        logger.info("Database refreshed")
    
    def status(self):
        """Показать статус миграций"""
        all_migrations = self._get_migration_files()
        applied = self.get_applied_migrations()
        
        logger.info("Migration status:")
        logger.info("-" * 50)
        
        for migration in all_migrations:
            status = "Applied" if migration in applied else "Pending"
            logger.info(f"{migration}: {status}")
        
        logger.info("-" * 50)
        logger.info(f"Total: {len(all_migrations)}, Applied: {len(applied)}, Pending: {len(all_migrations) - len(applied)}")
    
    def create_migration(self, name: str) -> str:
        """
        Создать новый файл миграции (как php artisan make:migration)
        
        Args:
            name: Название миграции (например: create_users_table)
            
        Returns:
            Путь к созданному файлу
        """
        # Создаём директорию если её нет
        self.migrations_path.mkdir(exist_ok=True)
        
        # Генерируем имя файла с timestamp
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        migration_name = f"{timestamp}_{name}"
        migration_file = self.migrations_path / f"{migration_name}.py"
        
        # Шаблон миграции
        template = f'''"""
Migration: {name}
Created at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from tgframework.orm import Migration, DatabaseEngine


class {self._to_class_name(name)}(Migration):
    """Migration class"""
    
    def up(self, engine: DatabaseEngine):
        """Apply migration"""
        # Определяем тип движка
        is_postgres = "postgresql" in engine.connection_string
        
        # Пример создания таблицы
        query = """
            CREATE TABLE IF NOT EXISTS example_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        
        # Адаптируем для PostgreSQL
        if is_postgres:
            query = query.replace("AUTOINCREMENT", "")
            query = query.replace("INTEGER PRIMARY KEY", "SERIAL PRIMARY KEY")
        
        engine.execute(query)
        engine.commit()
    
    def down(self, engine: DatabaseEngine):
        """Rollback migration"""
        engine.execute("DROP TABLE IF EXISTS example_table")
        engine.commit()
'''
        
        # Сохраняем файл
        migration_file.write_text(template)
        logger.info(f"Created migration: {migration_file}")
        
        return str(migration_file)
    
    def _to_class_name(self, snake_case: str) -> str:
        """Конвертировать snake_case в PascalCase"""
        return ''.join(word.capitalize() for word in snake_case.split('_'))
    
    def create_table_from_model(self, model: Type[Model]):
        """
        Создать таблицу из модели (для быстрого старта)
        DEPRECATED: Используйте миграции вместо этого
        """
        logger.warning("create_table_from_model is deprecated. Use migrations instead.")
        
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
        logger.info(f"Creating table: {query}")
        self.engine.execute(query)
        self.engine.commit()
        logger.info(f"Table {table_name} created")
