"""
Модели ORM
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime
from abc import ABCMeta


T = TypeVar('T', bound='Model')


class Field:
    """Базовый класс поля модели"""
    
    def __init__(self, 
                 primary_key: bool = False,
                 nullable: bool = False,
                 default: Any = None,
                 unique: bool = False,
                 index: bool = False):
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.index = index
        self.name: Optional[str] = None
    
    def get_sql_type(self, engine: str) -> str:
        """Получить SQL тип для поля"""
        raise NotImplementedError
    
    def to_db_value(self, value: Any) -> Any:
        """Преобразовать значение для сохранения в БД"""
        return value
    
    def from_db_value(self, value: Any) -> Any:
        """Преобразовать значение из БД"""
        return value


class IntegerField(Field):
    """Целочисленное поле"""
    
    def __init__(self, auto_increment=False, **kwargs):
        self.auto_increment = auto_increment
        super().__init__(**kwargs)
    
    def get_sql_type(self, engine: str) -> str:
        if engine == "sqlite":
            return "INTEGER"
        elif engine == "postgresql":
            if self.auto_increment:
                return "SERIAL"
            return "INTEGER"
        return "INTEGER"


class StringField(Field):
    """Строковое поле"""
    
    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
    
    def get_sql_type(self, engine: str) -> str:
        if engine == "postgresql":
            return f"VARCHAR({self.max_length})"
        return f"TEXT"


class TextField(Field):
    """Текстовое поле (большой текст)"""
    
    def get_sql_type(self, engine: str) -> str:
        return "TEXT"


class BooleanField(Field):
    """Булево поле"""
    
    def get_sql_type(self, engine: str) -> str:
        if engine == "sqlite":
            return "INTEGER"
        return "BOOLEAN"
    
    def to_db_value(self, value: Any) -> Any:
        if value is None:
            return None
        return int(bool(value))
    
    def from_db_value(self, value: Any) -> Any:
        if value is None:
            return None
        return bool(value)


class DateTimeField(Field):
    """Поле даты и времени"""
    
    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
    
    def get_sql_type(self, engine: str) -> str:
        if engine == "sqlite":
            return "TIMESTAMP"
        return "TIMESTAMP"
    
    def to_db_value(self, value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        return value
    
    def from_db_value(self, value: Any) -> Any:
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class ForeignKey(Field):
    """Внешний ключ"""
    
    def __init__(self, to: Type['Model'], on_delete: str = "CASCADE", **kwargs):
        super().__init__(**kwargs)
        self.to = to
        self.on_delete = on_delete
    
    def get_sql_type(self, engine: str) -> str:
        return "INTEGER"


class ModelMeta(ABCMeta):
    """Метакласс для моделей"""
    
    def __new__(mcs, name, bases, attrs):
        # Собираем поля
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                value.name = key
                fields[key] = value
        
        attrs['_fields'] = fields
        attrs['_table_name'] = attrs.get('_table_name', name.lower() + 's')
        
        return super().__new__(mcs, name, bases, attrs)


class Model(metaclass=ModelMeta):
    """Базовая модель ORM"""
    
    _fields: Dict[str, Field] = {}
    _table_name: str = ""
    _session: Optional['Session'] = None
    
    def __init__(self, **kwargs):
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name, field.default)
            setattr(self, field_name, value)
    
    @classmethod
    def get_table_name(cls) -> str:
        """Получить имя таблицы"""
        return cls._table_name
    
    @classmethod
    def get_fields(cls) -> Dict[str, Field]:
        """Получить поля модели"""
        return cls._fields
    
    @classmethod
    def get_primary_key_field(cls) -> Optional[Field]:
        """Получить поле первичного ключа"""
        for field in cls._fields.values():
            if field.primary_key:
                return field
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать модель в словарь"""
        result = {}
        for field_name in self._fields:
            result[field_name] = getattr(self, field_name, None)
        return result
    
    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Создать модель из словаря"""
        return cls(**data)
    
    def __repr__(self) -> str:
        fields_str = ", ".join(f"{k}={getattr(self, k, None)}" for k in self._fields)
        return f"<{self.__class__.__name__}({fields_str})>"

