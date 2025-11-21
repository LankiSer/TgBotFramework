# Примеры использования DDD/DTO в TgFramework 3.0

## Базовая структура

TgFramework 3.0 построен на принципах Domain-Driven Design (DDD) и использует Data Transfer Objects (DTO) для передачи данных между слоями.

## 1. Работа с пользователями

### Domain Model

```python
from tgframework.domain import User

# Domain модель содержит бизнес-логику
user = User(
    user_id=123,
    username="john",
    first_name="John",
    is_admin=False
)

# Бизнес-логика в модели
user.promote_to_admin()
```

### DTO (Data Transfer Objects)

```python
from tgframework.domain import UserDTO, CreateUserDTO, UpdateUserDTO

# DTO для создания
create_dto = CreateUserDTO(
    user_id=123,
    username="john",
    first_name="John"
)

# DTO для обновления
update_dto = UpdateUserDTO(
    username="john_new",
    first_name="John Updated"
)

# DTO для передачи данных
user_dto = UserDTO(
    user_id=123,
    username="john",
    first_name="John",
    last_name="Doe",
    is_admin=False
)
```

### Repository

```python
from tgframework.domain import UserRepository
from tgframework.orm import Session, create_engine

engine = create_engine("sqlite:///bot.db")
session = Session(engine)

# Репозиторий инкапсулирует доступ к данным
user_repo = UserRepository(session)

# CRUD операции
user = user_repo.get_by_id(123)
user = user_repo.create(create_dto)
user = user_repo.update(123, update_dto)
user_repo.delete(123)

# Поиск
users = user_repo.find_all()
user = user_repo.find_by_username("john")
```

### Service

```python
from tgframework.domain import UserService

# Сервис содержит бизнес-логику
user_service = UserService(user_repo)

# Получение пользователя (возвращает DTO)
user_dto = user_service.get_user(123)

# Создание пользователя
user_dto = user_service.create_user(create_dto)

# Обновление
user_dto = user_service.update_user(123, update_dto)

# Получение всех пользователей
users = user_service.get_all_users()

# Проверка админа
is_admin = user_service.is_admin(123)
```

## 2. Полный пример бота с DDD

```python
import asyncio
from tgframework import (
    TelegramBot,
    load_config,
    create_engine,
    Session,
    UserService,
    UserRepository,
    CreateUserDTO
)

async def main():
    # 1. Загрузка конфигурации
    config = load_config()
    
    # 2. Создание ORM engine
    engine = create_engine(config.database.connection_string)
    engine.connect()
    
    # 3. Создание session
    session = Session(engine)
    
    # 4. Создание repository
    user_repo = UserRepository(session)
    
    # 5. Создание service
    user_service = UserService(user_repo)
    
    # 6. Создание бота
    bot = TelegramBot(config.bot.token, session)
    
    # 7. Регистрация обработчика
    @bot.register_command("start")
    async def start_handler(update, context):
        user_data = context["user"]
        
        # Создаем DTO из данных Telegram
        create_dto = CreateUserDTO(
            user_id=user_data["id"],
            username=user_data.get("username"),
            first_name=user_data.get("first_name"),
            last_name=user_data.get("last_name")
        )
        
        # Используем сервис для создания/обновления пользователя
        user_dto = user_service.create_user(create_dto)
        
        # Отправка сообщения
        await bot.send_message(
            context["chat"]["id"],
            f"Привет, {user_dto.first_name}!"
        )
    
    # 8. Запуск бота
    await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
```

## 3. Пример с несколькими сущностями

```python
from tgframework import (
    UserService,
    ChatService,
    MessageService,
    UserRepository,
    ChatRepository,
    MessageRepository,
    CreateChatDTO,
    CreateMessageDTO
)

# Создание всех сервисов
user_service = UserService(UserRepository(session))
chat_service = ChatService(ChatRepository(session))
message_service = MessageService(MessageRepository(session))

# Обработчик сообщения
@bot.register_message_handler()
async def message_handler(update, context):
    # Получение данных
    user_id = context["user"]["id"]
    chat_id = context["chat"]["id"]
    message_text = update.get("text", "")
    
    # 1. Работа с пользователем через сервис
    user = user_service.get_user(user_id)
    if not user:
        user = user_service.create_user(CreateUserDTO(
            user_id=user_id,
            username=context["user"].get("username")
        ))
    
    # 2. Работа с чатом через сервис
    chat = chat_service.get_chat(chat_id)
    if not chat:
        chat = chat_service.create_chat(CreateChatDTO(
            chat_id=chat_id,
            chat_type=context["chat"]["type"],
            title=context["chat"].get("title")
        ))
    
    # 3. Сохранение сообщения через сервис
    message = message_service.create_message(CreateMessageDTO(
        message_id=update["message_id"],
        chat_id=chat_id,
        user_id=user_id,
        text=message_text
    ))
    
    # Бизнес-логика
    if message.text.startswith("/admin"):
        if user.is_admin:
            await bot.send_message(chat_id, "Admin command executed")
        else:
            await bot.send_message(chat_id, "Access denied")
```

## 4. Пример с веб-сервером

```python
from tgframework.web import Router, Controller
from tgframework.domain import UserService

class ApiController(Controller):
    def __init__(self, user_service: UserService):
        super().__init__()
        self.user_service = user_service
    
    async def get_users(self, request):
        """GET /api/users"""
        # Получаем всех пользователей через сервис
        users = self.user_service.get_all_users()
        
        # Преобразуем DTO в dict
        users_data = [
            {
                "user_id": u.user_id,
                "username": u.username,
                "first_name": u.first_name
            }
            for u in users
        ]
        
        return self.success({"users": users_data})
    
    async def get_user(self, request):
        """GET /api/users/{id}"""
        user_id = int(request.match_info["id"])
        
        # Получаем пользователя через сервис
        user = self.user_service.get_user(user_id)
        
        if not user:
            return self.error("User not found", status=404)
        
        return self.success({
            "user_id": user.user_id,
            "username": user.username,
            "first_name": user.first_name
        })

# Настройка роутинга
router = Router()
controller = ApiController(user_service)

router.get("/api/users", controller.get_users)
router.get("/api/users/{id}", controller.get_user)
```

## 5. Пример с транзакциями

```python
from tgframework.orm import Session

async def transfer_admin_rights(
    from_user_id: int,
    to_user_id: int,
    user_service: UserService
):
    """Передача прав администратора"""
    
    # Начало транзакции
    with Session.transaction():
        # 1. Получаем пользователей
        from_user = user_service.get_user(from_user_id)
        to_user = user_service.get_user(to_user_id)
        
        if not from_user or not to_user:
            raise ValueError("User not found")
        
        if not from_user.is_admin:
            raise ValueError("From user is not admin")
        
        # 2. Обновляем статусы
        user_service.update_user(from_user_id, UpdateUserDTO(is_admin=False))
        user_service.update_user(to_user_id, UpdateUserDTO(is_admin=True))
        
        # Транзакция автоматически коммитится
        # Если ошибка - автоматически откатывается
```

## 6. Создание своих Domain моделей

```python
from tgframework.orm import Model, IntegerField, StringField, DateTimeField

# 1. Domain модель
class Product(Model):
    __tablename__ = "products"
    
    id = IntegerField(primary_key=True, autoincrement=True)
    name = StringField(max_length=255, nullable=False)
    price = IntegerField(nullable=False)
    created_at = DateTimeField(auto_now_add=True)
    
    def apply_discount(self, percent: int):
        """Бизнес-логика в модели"""
        self.price = int(self.price * (100 - percent) / 100)

# 2. DTO
from dataclasses import dataclass

@dataclass
class ProductDTO:
    id: int
    name: str
    price: int
    
@dataclass
class CreateProductDTO:
    name: str
    price: int

# 3. Repository
from tgframework.orm import Session
from typing import Optional, List

class ProductRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.session.get(Product, product_id)
    
    def create(self, dto: CreateProductDTO) -> Product:
        product = Product(name=dto.name, price=dto.price)
        return self.session.add(product)
    
    def find_all(self) -> List[Product]:
        return self.session.query(Product).all()

# 4. Service
class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo
    
    def get_product(self, product_id: int) -> Optional[ProductDTO]:
        product = self.repo.get_by_id(product_id)
        return self._to_dto(product) if product else None
    
    def create_product(self, dto: CreateProductDTO) -> ProductDTO:
        product = self.repo.create(dto)
        return self._to_dto(product)
    
    def _to_dto(self, product: Product) -> ProductDTO:
        return ProductDTO(
            id=product.id,
            name=product.name,
            price=product.price
        )
```

## 7. Использование в боте

```python
# Создаем сервис
product_repo = ProductRepository(session)
product_service = ProductService(product_repo)

@bot.register_command("products")
async def show_products(update, context):
    # Получаем все продукты через сервис
    products = product_service.get_all_products()
    
    # Формируем сообщение
    message = "Список товаров:\n\n"
    for product in products:
        message += f"{product.name} - {product.price} руб.\n"
    
    await bot.send_message(context["chat"]["id"], message)

@bot.register_command("buy")
async def buy_product(update, context):
    # Парсим ID товара
    product_id = int(context.get("args", [0])[0])
    
    # Получаем товар через сервис
    product = product_service.get_product(product_id)
    
    if not product:
        await bot.send_message(
            context["chat"]["id"],
            "Товар не найден"
        )
        return
    
    # Бизнес-логика покупки
    user_id = context["user"]["id"]
    order_service.create_order(user_id, product_id)
    
    await bot.send_message(
        context["chat"]["id"],
        f"Вы купили {product.name} за {product.price} руб."
    )
```

## Преимущества DDD/DTO

1. **Чистый код**: Каждый слой имеет свою ответственность
2. **Тестируемость**: Легко писать unit-тесты
3. **Масштабируемость**: Легко добавлять новые функции
4. **Поддерживаемость**: Понятная структура
5. **Безопасность**: DTO защищают от инъекций

## Заключение

DDD/DTO паттерны делают код:
- Более организованным
- Легче в поддержке
- Проще в тестировании
- Безопаснее в использовании

TgFramework 3.0 предоставляет все инструменты для профессиональной разработки!

