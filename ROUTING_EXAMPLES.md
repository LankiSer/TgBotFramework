# Примеры использования роутинга

## Роутинг в стиле Laravel

### Создание собственного контроллера

```python
from tgframework.web import Controller

class ProductController(Controller):
    """Контроллер для работы с продуктами"""
    
    def __init__(self, session=None):
        super().__init__()
        self.session = session
    
    async def index(self, request):
        """GET /products - список продуктов"""
        products = [
            {"id": 1, "name": "Product 1", "price": 100},
            {"id": 2, "name": "Product 2", "price": 200},
        ]
        return self.success(products)
    
    async def show(self, request, id: str):
        """GET /products/{id} - детали продукта"""
        product = {"id": id, "name": f"Product {id}", "price": 100}
        return self.success(product)
    
    async def store(self, request):
        """POST /products - создать продукт"""
        data = await request.json()
        return self.success(data, "Product created")
    
    async def update(self, request, id: str):
        """PUT /products/{id} - обновить продукт"""
        data = await request.json()
        return self.success(data, "Product updated")
    
    async def destroy(self, request, id: str):
        """DELETE /products/{id} - удалить продукт"""
        return self.success(None, "Product deleted")
```

### Регистрация маршрутов

```python
from tgframework.web import Router
from controllers.product_controller import ProductController

router = Router()
product_controller = ProductController(session)

# Вариант 1: Вручную
router.get("/products", product_controller.index, name="products.index")
router.get("/products/{id}", product_controller.show, name="products.show")
router.post("/products", product_controller.store, name="products.store")
router.put("/products/{id}", product_controller.update, name="products.update")
router.delete("/products/{id}", product_controller.destroy, name="products.destroy")

# Вариант 2: RESTful resource (автоматически)
router.resource("/products", product_controller, name_prefix="products")

# Применить к приложению
router.apply_routes(app)
```

### Группировка маршрутов

```python
from tgframework.web import Router

router = Router()

# Группа API маршрутов
with router.group(prefix="/api"):
    router.get("/users", users_controller.index)
    router.get("/users/{id}", users_controller.show)
    
    # Подгруппа с дополнительным префиксом
    with router.group(prefix="/admin"):
        router.get("/stats", admin_controller.stats)
        # Результат: /api/admin/stats

# Группа с middleware
async def auth_middleware(request):
    # Проверка авторизации
    if not request.cookies.get('token'):
        return web.Response(status=401, text="Unauthorized")

with router.group(middleware=[auth_middleware]):
    router.get("/protected", protected_controller.index)
    router.post("/protected/action", protected_controller.action)
```

### Использование декораторов

```python
from tgframework.web import Router

router = Router()

@router.get("/hello")
async def hello(request):
    return {"message": "Hello World"}

@router.post("/users")
async def create_user(request):
    data = await request.json()
    # Создание пользователя
    return {"success": True, "user": data}

@router.get("/users/{id}")
async def get_user(request, id: str):
    return {"id": id, "name": f"User {id}"}
```

## Встроенные API endpoints

### API для пользователей

```bash
# Список пользователей
GET /api/users

# Информация о пользователе
GET /api/users/{id}

# Статистика
GET /api/stats

# Отправить сообщение
POST /api/send
{
  "chat_id": 123456,
  "text": "Hello"
}
```

### Mini App endpoints

```bash
# Главная страница Mini App
GET /miniapp

# Валидация данных Mini App
POST /miniapp/validate
{
  "initData": "telegram_init_data_string"
}

# Получить данные пользователя
POST /miniapp/user
{
  "initData": "telegram_init_data_string"
}

# Отправить данные из Mini App
POST /miniapp/send
{
  "initData": "telegram_init_data_string",
  "payload": {"action": "buy", "product_id": 123}
}
```

### Admin endpoints

```bash
# Админ-панель
GET /admin

# Вход
GET /admin/login

# Авторизация через Telegram
GET /admin/auth?id=...&first_name=...&hash=...

# Список пользователей (требует авторизации)
GET /admin/users

# Выход
POST /admin/logout
```

## Пример полного приложения

```python
import asyncio
from aiohttp import web
from tgframework import load_config, create_engine, Session, TelegramBot
from tgframework.web import Router, Controller, WebServer

# Конфигурация
config = load_config()
engine = create_engine(config.database.connection_string)
engine.connect()
session = Session(engine)
bot = TelegramBot(config.bot.token, session)

# Кастомный контроллер
class ShopController(Controller):
    def __init__(self, session):
        super().__init__()
        self.session = session
    
    async def products(self, request):
        products = [
            {"id": 1, "name": "Laptop", "price": 1000},
            {"id": 2, "name": "Phone", "price": 500},
        ]
        return self.success(products)
    
    async def buy(self, request):
        data = await request.json()
        product_id = data.get("product_id")
        user_id = data.get("user_id")
        
        # Логика покупки
        return self.success({
            "order_id": 123,
            "product_id": product_id,
            "status": "processing"
        }, "Order created")

# Создание роутера
router = Router()
shop_controller = ShopController(session)

# API routes
with router.group(prefix="/api/shop"):
    router.get("/products", shop_controller.products)
    router.post("/buy", shop_controller.buy)

# Веб-сервер
web_server = WebServer(config, session, bot)

async def main():
    # Запуск веб-сервера
    await web_server.start()
    
    # Запуск бота
    await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
```

## Response helpers

Контроллеры имеют встроенные методы для ответов:

```python
class MyController(Controller):
    async def example(self, request):
        # JSON ответ
        return self.json({"key": "value"})
        
        # Успешный ответ
        return self.success(data, "Operation successful")
        
        # Ошибка
        return self.error("Something went wrong", status=400)
        
        # Редирект
        return self.redirect("/other-page")
        
        # View (в будущем будет с шаблонизатором)
        return self.view("template.html", {"data": "value"})
```

## Middleware

```python
async def logging_middleware(request):
    print(f"Request: {request.method} {request.path}")
    # None = продолжить обработку
    # Response = прервать и вернуть ответ

async def auth_middleware(request):
    token = request.headers.get("Authorization")
    if not token:
        return web.Response(status=401, text="Unauthorized")

# Применить к конкретным маршрутам
router.get("/protected", handler, middleware=[auth_middleware])

# Применить к группе
with router.group(middleware=[auth_middleware, logging_middleware]):
    router.get("/admin/users", admin.users)
    router.post("/admin/action", admin.action)
```

Всё готово! Роутинг работает как в Laravel с контроллерами, группировкой, middleware и RESTful ресурсами.

