"""
Система роутинга в стиле Laravel
"""

from typing import Callable, Dict, List, Optional, Any
from aiohttp import web
import functools
import inspect


class Route:
    """Класс маршрута"""
    
    def __init__(self, method: str, path: str, handler: Callable, name: Optional[str] = None, middleware: List[Callable] = None):
        self.method = method.upper()
        self.path = path
        self.handler = handler
        self.name = name or f"{method}_{path}".replace("/", "_")
        self.middleware = middleware or []


class Router:
    """Роутер в стиле Laravel"""
    
    def __init__(self):
        self.routes: List[Route] = []
        self.middleware_stack: List[Callable] = []
        self.route_groups: List[Dict[str, Any]] = []
    
    def add_route(self, method: str, path: str, handler: Callable, name: Optional[str] = None, middleware: List[Callable] = None):
        """Добавить маршрут"""
        # Применяем групповые префиксы
        for group in self.route_groups:
            if "prefix" in group:
                path = group["prefix"] + path
            if "middleware" in group:
                middleware = (middleware or []) + group["middleware"]
        
        route = Route(method, path, handler, name, middleware)
        self.routes.append(route)
        return route
    
    def get(self, path: str, handler: Callable = None, name: Optional[str] = None, middleware: List[Callable] = None):
        """GET маршрут"""
        if handler is None:
            def decorator(func: Callable):
                self.add_route("GET", path, func, name, middleware)
                return func
            return decorator
        return self.add_route("GET", path, handler, name, middleware)
    
    def post(self, path: str, handler: Callable = None, name: Optional[str] = None, middleware: List[Callable] = None):
        """POST маршрут"""
        if handler is None:
            def decorator(func: Callable):
                self.add_route("POST", path, func, name, middleware)
                return func
            return decorator
        return self.add_route("POST", path, handler, name, middleware)
    
    def put(self, path: str, handler: Callable = None, name: Optional[str] = None, middleware: List[Callable] = None):
        """PUT маршрут"""
        if handler is None:
            def decorator(func: Callable):
                self.add_route("PUT", path, func, name, middleware)
                return func
            return decorator
        return self.add_route("PUT", path, handler, name, middleware)
    
    def delete(self, path: str, handler: Callable = None, name: Optional[str] = None, middleware: List[Callable] = None):
        """DELETE маршрут"""
        if handler is None:
            def decorator(func: Callable):
                self.add_route("DELETE", path, func, name, middleware)
                return func
            return decorator
        return self.add_route("DELETE", path, handler, name, middleware)
    
    def group(self, prefix: str = None, middleware: List[Callable] = None):
        """Группировка маршрутов"""
        class RouteGroup:
            def __init__(self, router: Router, prefix: Optional[str], middleware: Optional[List[Callable]]):
                self.router = router
                self.group_config = {}
                if prefix:
                    self.group_config["prefix"] = prefix
                if middleware:
                    self.group_config["middleware"] = middleware
            
            def __enter__(self):
                self.router.route_groups.append(self.group_config)
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.router.route_groups.pop()
        
        return RouteGroup(self, prefix, middleware)
    
    def resource(self, path: str, controller: Any, name_prefix: Optional[str] = None):
        """RESTful resource маршруты"""
        name_prefix = name_prefix or path.strip("/").replace("/", ".")
        
        # index - GET /resource
        if hasattr(controller, "index"):
            self.get(path, controller.index, f"{name_prefix}.index")
        
        # create - GET /resource/create
        if hasattr(controller, "create"):
            self.get(f"{path}/create", controller.create, f"{name_prefix}.create")
        
        # store - POST /resource
        if hasattr(controller, "store"):
            self.post(path, controller.store, f"{name_prefix}.store")
        
        # show - GET /resource/{id}
        if hasattr(controller, "show"):
            self.get(f"{path}/{{id}}", controller.show, f"{name_prefix}.show")
        
        # edit - GET /resource/{id}/edit
        if hasattr(controller, "edit"):
            self.get(f"{path}/{{id}}/edit", controller.edit, f"{name_prefix}.edit")
        
        # update - PUT /resource/{id}
        if hasattr(controller, "update"):
            self.put(f"{path}/{{id}}", controller.update, f"{name_prefix}.update")
        
        # destroy - DELETE /resource/{id}
        if hasattr(controller, "destroy"):
            self.delete(f"{path}/{{id}}", controller.destroy, f"{name_prefix}.destroy")
    
    def apply_routes(self, app: web.Application):
        """Применить маршруты к приложению aiohttp"""
        for route in self.routes:
            handler = self._wrap_handler(route)
            
            if route.method == "GET":
                app.router.add_get(route.path, handler, name=route.name)
            elif route.method == "POST":
                app.router.add_post(route.path, handler, name=route.name)
            elif route.method == "PUT":
                app.router.add_put(route.path, handler, name=route.name)
            elif route.method == "DELETE":
                app.router.add_delete(route.path, handler, name=route.name)
    
    def _wrap_handler(self, route: Route) -> Callable:
        """Обернуть обработчик с middleware"""
        async def wrapped_handler(request: web.Request) -> web.Response:
            # Применяем middleware
            for middleware in route.middleware:
                result = await middleware(request)
                if isinstance(result, web.Response):
                    return result
            
            # Вызываем основной обработчик
            # Проверяем сигнатуру: если принимает только request - вызываем так
            sig = inspect.signature(route.handler)
            params = list(sig.parameters.keys())
            
            if len(params) == 1:
                response = await route.handler(request)
            else:
                # Иначе передаем дополнительные параметры из match_info
                response = await route.handler(request, **request.match_info)
            
            # Если вернули dict - конвертируем в JSON
            if isinstance(response, dict):
                return web.json_response(response)
            
            # Если вернули строку - конвертируем в Response
            if isinstance(response, str):
                return web.Response(text=response, content_type="text/html")
            
            return response
        
        return wrapped_handler


class Controller:
    """Базовый класс контроллера"""
    
    def __init__(self):
        self.request: Optional[web.Request] = None
    
    def json(self, data: Any, status: int = 200) -> web.Response:
        """Вернуть JSON ответ"""
        return web.json_response(data, status=status)
    
    def success(self, data: Any = None, message: str = "Success") -> web.Response:
        """Вернуть успешный ответ"""
        return self.json({
            "success": True,
            "message": message,
            "data": data
        })
    
    def error(self, message: str, status: int = 400) -> web.Response:
        """Вернуть ошибку"""
        return self.json({
            "success": False,
            "message": message
        }, status=status)
    
    def redirect(self, url: str) -> web.Response:
        """Редирект"""
        return web.HTTPFound(url)
    
    def view(self, template: str, context: Dict[str, Any] = None) -> web.Response:
        """Вернуть view (будет реализовано через шаблонизатор)"""
        # TODO: интеграция с шаблонизатором
        return web.Response(text=f"View: {template}", content_type="text/html")


# Глобальный роутер
router = Router()

