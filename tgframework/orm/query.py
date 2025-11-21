"""
Query Builder для ORM
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from .models import Model


T = TypeVar('T', bound=Model)


class QueryBuilder:
    """Построитель запросов"""
    
    def __init__(self, model: Type[T], engine):
        self.model = model
        self.engine = engine
        self._where_clauses: List[str] = []
        self._where_params: List[Any] = []
        self._order_by: List[str] = []
        self._limit_value: Optional[int] = None
        self._offset_value: Optional[int] = None
    
    def where(self, **conditions) -> 'QueryBuilder':
        """Добавить условие WHERE"""
        for field, value in conditions.items():
            self._where_clauses.append(f"{field} = ?")
            self._where_params.append(value)
        return self
    
    def order_by(self, *fields: str) -> 'QueryBuilder':
        """Добавить сортировку"""
        self._order_by.extend(fields)
        return self
    
    def limit(self, limit: int) -> 'QueryBuilder':
        """Установить лимит"""
        self._limit_value = limit
        return self
    
    def offset(self, offset: int) -> 'QueryBuilder':
        """Установить смещение"""
        self._offset_value = offset
        return self
    
    def build_select_query(self) -> tuple[str, tuple]:
        """Построить SELECT запрос"""
        table_name = self.model.get_table_name()
        query = f"SELECT * FROM {table_name}"
        
        if self._where_clauses:
            query += " WHERE " + " AND ".join(self._where_clauses)
        
        if self._order_by:
            query += " ORDER BY " + ", ".join(self._order_by)
        
        if self._limit_value:
            query += f" LIMIT {self._limit_value}"
        
        if self._offset_value:
            query += f" OFFSET {self._offset_value}"
        
        return query, tuple(self._where_params)
    
    def all(self) -> List[T]:
        """Получить все записи"""
        query, params = self.build_select_query()
        rows = self.engine.fetchall(query, params)
        return [self.model.from_dict(row) for row in rows]
    
    def first(self) -> Optional[T]:
        """Получить первую запись"""
        self.limit(1)
        query, params = self.build_select_query()
        row = self.engine.fetchone(query, params)
        if row:
            return self.model.from_dict(row)
        return None
    
    def get(self, **conditions) -> Optional[T]:
        """Получить одну запись по условию"""
        return self.where(**conditions).first()
    
    def count(self) -> int:
        """Посчитать количество записей"""
        table_name = self.model.get_table_name()
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        
        if self._where_clauses:
            query += " WHERE " + " AND ".join(self._where_clauses)
        
        row = self.engine.fetchone(query, tuple(self._where_params))
        return row['count'] if row else 0

