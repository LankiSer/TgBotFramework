"""
Сессия для работы с БД
"""

from typing import Type, TypeVar, Optional, List
from .models import Model
from .query import QueryBuilder
from .engine import DatabaseEngine


T = TypeVar('T', bound=Model)


class Session:
    """Сессия для работы с БД"""
    
    def __init__(self, engine: DatabaseEngine):
        self.engine = engine
        self._in_transaction = False
    
    def query(self, model: Type[T]) -> QueryBuilder:
        """Создать запрос для модели"""
        return QueryBuilder(model, self.engine)
    
    def add(self, instance: Model):
        """Добавить объект в БД"""
        table_name = instance.get_table_name()
        fields = instance.get_fields()
        
        # Собираем данные для вставки
        columns = []
        values = []
        placeholders = []
        
        for field_name, field in fields.items():
            # Пропускаем auto_increment поля
            if hasattr(field, 'auto_increment') and field.auto_increment:
                continue
            
            value = getattr(instance, field_name, field.default)
            if value is not None or not field.nullable:
                columns.append(field_name)
                values.append(field.to_db_value(value))
                placeholders.append("?")
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor = self.engine.execute(query, tuple(values))
        
        # Получаем ID вставленной записи
        if hasattr(cursor, 'lastrowid'):
            pk_field = instance.get_primary_key_field()
            if pk_field:
                setattr(instance, pk_field.name, cursor.lastrowid)
        
        if not self._in_transaction:
            self.engine.commit()
        
        return instance
    
    def update(self, instance: Model):
        """Обновить объект в БД"""
        table_name = instance.get_table_name()
        fields = instance.get_fields()
        pk_field = instance.get_primary_key_field()
        
        if not pk_field:
            raise ValueError("Модель не имеет первичного ключа")
        
        pk_value = getattr(instance, pk_field.name)
        if pk_value is None:
            raise ValueError("Первичный ключ не установлен")
        
        # Собираем данные для обновления
        set_clauses = []
        values = []
        
        for field_name, field in fields.items():
            if field.primary_key:
                continue
            
            value = getattr(instance, field_name)
            set_clauses.append(f"{field_name} = ?")
            values.append(field.to_db_value(value))
        
        values.append(pk_value)
        
        query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {pk_field.name} = ?"
        self.engine.execute(query, tuple(values))
        
        if not self._in_transaction:
            self.engine.commit()
        
        return instance
    
    def delete(self, instance: Model):
        """Удалить объект из БД"""
        table_name = instance.get_table_name()
        pk_field = instance.get_primary_key_field()
        
        if not pk_field:
            raise ValueError("Модель не имеет первичного ключа")
        
        pk_value = getattr(instance, pk_field.name)
        if pk_value is None:
            raise ValueError("Первичный ключ не установлен")
        
        query = f"DELETE FROM {table_name} WHERE {pk_field.name} = ?"
        self.engine.execute(query, (pk_value,))
        
        if not self._in_transaction:
            self.engine.commit()
    
    def get(self, model: Type[T], pk: int) -> Optional[T]:
        """Получить объект по первичному ключу"""
        pk_field = model.get_primary_key_field()
        if not pk_field:
            raise ValueError("Модель не имеет первичного ключа")
        
        return self.query(model).where(**{pk_field.name: pk}).first()
    
    def all(self, model: Type[T]) -> List[T]:
        """Получить все объекты"""
        return self.query(model).all()
    
    def begin(self):
        """Начать транзакцию"""
        self._in_transaction = True
    
    def commit(self):
        """Зафиксировать транзакцию"""
        self.engine.commit()
        self._in_transaction = False
    
    def rollback(self):
        """Откатить транзакцию"""
        self.engine.rollback()
        self._in_transaction = False
    
    def close(self):
        """Закрыть сессию"""
        self.engine.disconnect()

