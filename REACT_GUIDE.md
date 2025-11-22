# React + TypeScript в TgFramework 3.1.2

Полное руководство по использованию React + TypeScript в TgFramework.

## Быстрый старт

### 1. Создание проекта

```bash
# С React (по умолчанию)
tgframework create-project my_bot

# Без React
tgframework create-project my_bot --no-react
```

### 2. Установка зависимостей

```bash
cd my_bot

# Python
pip install tgframework-bot python-dotenv

# React (если с frontend)
cd frontend
npm install
cd ..
```

### 3. Настройка

`.env`:
```env
BOT_TOKEN=your_bot_token
WEB_ENABLED=true
WEB_PORT=8080
```

### 4. Сборка frontend

```bash
cd frontend
npm run build  # Production
# или
npm run dev    # Development (localhost:3000)
```

### 5. Запуск

```bash
python main.py
```

## Структура проекта

```
my_bot/
├── frontend/              # React + TypeScript
│   ├── src/
│   │   ├── main.tsx      # Точка входа
│   │   ├── App.tsx       # Главный компонент
│   │   ├── components/   # React компоненты
│   │   │   ├── Header.tsx
│   │   │   ├── Profile.tsx
│   │   │   ├── Stats.tsx
│   │   │   └── ActionGrid.tsx
│   │   ├── hooks/
│   │   │   └── useTelegramWebApp.ts
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
├── app/
│   ├── web/
│   │   ├── controllers.py      # Python контроллеры
│   │   └── static/dist/        # Собранный React
│   └── handlers/               # Bot handlers
└── main.py
```

## React Renderer

### Базовое использование

```python
from tgframework.miniapp import ReactRenderer, get_telegram_user_photo_url

# Инициализация
renderer = ReactRenderer('/path/to/build', title="My Bot")

# Рендеринг с props
props = {
    'user': {
        'user_id': 123,
        'first_name': 'John',
        'photo_url': get_telegram_user_photo_url(bot_token, 123)
    },
    'page': 'home'
}

return renderer.render(props)
```

### Полный пример контроллера

```python
# -*- coding: utf-8 -*-
from aiohttp import web
from tgframework.web import Controller
from tgframework.miniapp import ReactRenderer, get_telegram_user_photo_url

class WebController(Controller):
    def __init__(self, user_service, bot_token):
        super().__init__()
        self.user_service = user_service
        self.bot_token = bot_token
        
        # Путь к собранному React
        build_dir = 'app/web/static/dist'
        self.renderer = ReactRenderer(build_dir)
    
    async def index(self, request):
        """GET / - Главная страница"""
        user_id = request.query.get('user_id')
        
        props = {'page': 'home'}
        
        if user_id:
            user = self.user_service.get_user(int(user_id))
            if user:
                # Получаем аватарку из Telegram
                photo_url = get_telegram_user_photo_url(
                    self.bot_token, 
                    user.user_id
                )
                
                props['user'] = {
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'username': user.username,
                    'is_admin': user.is_admin,
                    'photo_url': photo_url
                }
        
        return self.renderer.render(props)
    
    async def profile(self, request):
        """GET /profile"""
        user_id = int(request.query.get('user_id'))
        user = self.user_service.get_user(user_id)
        
        props = {
            'page': 'profile',
            'user': {
                'user_id': user.user_id,
                'first_name': user.first_name,
                'photo_url': get_telegram_user_photo_url(
                    self.bot_token, 
                    user.user_id
                )
            }
        }
        
        return self.renderer.render(props, title=f"Профиль - {user.first_name}")
```

### Регистрация маршрутов

```python
def setup_routes(web_server, user_service, bot_token):
    controller = WebController(user_service, bot_token)
    
    app = web_server.app
    app.router.add_get('/', controller.index)
    app.router.add_get('/profile', controller.profile)
    
    # Статические файлы
    app.router.add_static('/static', 'app/web/static', name='static')
```

## React компоненты

### Получение server props

```tsx
// main.tsx
const serverProps = (window as any).__SERVER_PROPS__ || {};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App {...serverProps} />
  </React.StrictMode>,
)
```

### Типизация props

```tsx
// App.tsx
export interface User {
  user_id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  is_admin: boolean
}

export interface ServerProps {
  user?: User
  stats?: any
  page?: string
}

function App(props: ServerProps) {
  const [user, setUser] = useState<User | undefined>(props.user)
  // ...
}
```

### Telegram Web App hook

```tsx
import { useTelegramWebApp } from './hooks/useTelegramWebApp'

function App(props: ServerProps) {
  const tg = useTelegramWebApp()
  
  useEffect(() => {
    if (tg) {
      tg.ready()
      tg.expand()
      
      // Получаем данные пользователя
      const tgUser = tg.initDataUnsafe?.user
      if (tgUser) {
        setUser({
          user_id: tgUser.id,
          first_name: tgUser.first_name,
          photo_url: tgUser.photo_url
        })
      }
    }
  }, [tg])
}
```

### Отображение аватарки

```tsx
{user.photo_url ? (
  <img 
    src={user.photo_url} 
    alt={user.first_name} 
    className="user-avatar" 
  />
) : (
  <div className="user-avatar-placeholder">
    {user.first_name[0]}
  </div>
)}
```

## API запросы

### Из React в Python

```tsx
import axios from 'axios'

// GET запрос
const response = await axios.get('/api/stats')
const data = response.data

// POST запрос
await axios.post('/api/user/update', {
  user_id: user.id,
  first_name: user.first_name
})
```

### Python API контроллер

```python
class ApiController(Controller):
    async def get_stats(self, request):
        stats = {
            'total_users': self.user_service.get_user_count(),
            'messages': 0
        }
        return self.success(stats)
    
    async def update_user(self, request):
        data = await request.json()
        user_id = data['user_id']
        # Обновляем пользователя
        return self.success({'updated': True})
```

## Сборка и deploy

### Development

```bash
cd frontend
npm run dev  # localhost:3000 с hot reload
```

Vite автоматически проксирует `/api/*` на `http://localhost:8080`

### Production

```bash
cd frontend
npm run build
```

Файлы попадут в `app/web/static/dist/`:
- `assets/main-*.js` - JavaScript
- `assets/main-*.css` - CSS  
- `manifest.json` - Манифест

### Watch mode

```bash
cd frontend
npm run watch  # Автоматическая пересборка
```

## Получение аватарки из Telegram

```python
from tgframework.miniapp import get_telegram_user_photo_url

# Получить URL аватарки
photo_url = get_telegram_user_photo_url(bot_token, user_id)

# Использовать в props
props['user']['photo_url'] = photo_url
```

Функция автоматически:
1. Запрашивает фото через `getUserProfilePhotos`
2. Получает `file_id` первого фото
3. Запрашивает путь через `getFile`
4. Возвращает полный URL

## Стилизация

### CSS Variables

```css
:root {
  --primary-color: #0088cc;
  --secondary-color: #64b5f6;
  --bg-color: #f5f5f5;
  --card-bg: #ffffff;
  --border-radius: 12px;
}
```

### Responsive

```css
@media (max-width: 768px) {
  .action-grid {
    grid-template-columns: 1fr;
  }
}
```

## Telegram Mini App

### Конфигурация

`.env`:
```env
MINIAPP_ENABLED=true
MINIAPP_URL=https://yourbot.com
```

### Bot Setup

```python
from aiogram import types

# Кнопка с Mini App
keyboard = types.InlineKeyboardMarkup()
keyboard.add(
    types.InlineKeyboardButton(
        "Открыть приложение",
        web_app=types.WebAppInfo(url="https://yourbot.com")
    )
)
```

### Валидация данных

```python
from tgframework.miniapp import MiniAppValidator

validator = MiniAppValidator(bot_token)

@app.post('/miniapp/validate')
async def validate(request):
    init_data = await request.text()
    if validator.validate_init_data(init_data):
        return {'valid': True}
    return {'valid': False}
```

## Примеры компонентов

### Header с аватаркой

```tsx
export const Header: React.FC<{user?: User}> = ({ user }) => {
  return (
    <header className="header">
      <h1 className="logo">🤖 My Bot</h1>
      {user && (
        <div className="user-info">
          {user.photo_url ? (
            <img src={user.photo_url} alt={user.first_name} />
          ) : (
            <div className="avatar-placeholder">
              {user.first_name[0]}
            </div>
          )}
          <span>{user.first_name}</span>
        </div>
      )}
    </header>
  )
}
```

### Profile страница

```tsx
export const Profile: React.FC<{user: User}> = ({ user }) => {
  return (
    <div className="profile">
      <div className="profile-header">
        <img src={user.photo_url} />
      </div>
      <div className="profile-info">
        <h2>{user.first_name} {user.last_name}</h2>
        {user.username && <p>@{user.username}</p>}
        <p>ID: {user.user_id}</p>
      </div>
    </div>
  )
}
```

## Troubleshooting

### Проблема: Пустой экран

**Решение:** Проверьте, что React собран:
```bash
cd frontend
npm run build
```

### Проблема: 404 на статику

**Решение:** Проверьте регистрацию static routes:
```python
app.router.add_static('/static', 'app/web/static', name='static')
```

### Проблема: Кириллица не отображается

**Решение:** Используйте `charset='utf-8'`:
```python
return web.Response(text=html, charset='utf-8')
```

### Проблема: CORS ошибки

**Решение:** В `vite.config.ts` настроен прокси для `/api/*`

## Best Practices

1. **Типизация**: Всегда типизируйте props и state
2. **Server Props**: Передавайте только необходимые данные
3. **Аватарки**: Кешируйте URL аватарок
4. **API**: Используйте axios interceptors для обработки ошибок
5. **Стили**: Используйте CSS modules или styled-components
6. **Производительность**: Используйте React.memo для тяжелых компонентов

## Документация

- [TgFramework](https://github.com/LankiSer/TgBotFramework)
- [React](https://react.dev)
- [TypeScript](https://www.typescriptlang.org)
- [Vite](https://vitejs.dev)
- [Telegram Mini Apps](https://core.telegram.org/bots/webapps)

## Заключение

TgFramework 3.1.2 предоставляет полную интеграцию React + TypeScript с:
- ✅ Server-Side Props из Python
- ✅ Автоматическое получение аватарок
- ✅ TypeScript типизация
- ✅ Hot Module Replacement
- ✅ Production оптимизация
- ✅ Telegram Web App SDK

Создавайте современные веб-приложения для Telegram ботов! 🚀

