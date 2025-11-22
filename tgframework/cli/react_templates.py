# -*- coding: utf-8 -*-
"""
Шаблоны для React + TypeScript проектов
"""


PACKAGE_JSON = """{
  "name": "{project_name}-frontend",
  "version": "1.0.0",
  "description": "React + TypeScript frontend for Telegram Bot",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "watch": "vite build --watch"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0"
  }
}
"""

TSCONFIG_JSON = """{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"""

TSCONFIG_NODE_JSON = """{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
"""

VITE_CONFIG_TS = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../app/web/static/dist',
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: './src/main.tsx'
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      }
    }
  }
})
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

MAIN_TSX = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

const serverProps = (window as any).__SERVER_PROPS__ || {};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App {...serverProps} />
  </React.StrictMode>,
)
"""

APP_TSX = """import { useEffect, useState } from 'react'
import { useTelegramWebApp } from './hooks/useTelegramWebApp'
import { Header } from './components/Header'
import { Profile } from './components/Profile'
import { Stats } from './components/Stats'
import { ActionGrid } from './components/ActionGrid'
import './App.css'

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
  const tg = useTelegramWebApp()
  const [user, setUser] = useState<User | undefined>(props.user)
  const [page, setPage] = useState<string>(props.page || 'home')

  useEffect(() => {
    if (tg) {
      tg.ready()
      tg.expand()
      
      const tgUser = tg.initDataUnsafe?.user
      if (tgUser && !user) {
        setUser({
          user_id: tgUser.id,
          first_name: tgUser.first_name,
          last_name: tgUser.last_name,
          username: tgUser.username,
          photo_url: tgUser.photo_url,
          is_admin: false
        })
      }
    }
  }, [tg])

  const renderPage = () => {
    switch (page) {
      case 'profile':
        return <Profile user={user} />
      case 'stats':
        return <Stats user={user} stats={props.stats} />
      default:
        return (
          <div className="welcome-section">
            <div className="welcome-card">
              {user ? (
                <>
                  <h1 className="welcome-title">Привет, {user.first_name}! 👋</h1>
                  <p className="welcome-text">Добро пожаловать в веб-интерфейс бота</p>
                  
                  <div className="user-card">
                    <div className="user-card-header">
                      {user.photo_url ? (
                        <img src={user.photo_url} alt={user.first_name} className="user-card-avatar" />
                      ) : (
                        <div className="user-card-avatar-placeholder">{user.first_name[0]}</div>
                      )}
                      <div className="user-card-info">
                        <h3>{user.first_name} {user.last_name || ''}</h3>
                        {user.username && <p>@{user.username}</p>}
                      </div>
                    </div>
                  </div>

                  <ActionGrid user={user} onNavigate={setPage} />
                </>
              ) : (
                <>
                  <h1 className="welcome-title">Добро пожаловать! 👋</h1>
                  <p className="welcome-text">Откройте это приложение через Telegram бота</p>
                </>
              )}
            </div>
          </div>
        )
    }
  }

  return (
    <div className="app">
      <Header user={user} onNavigate={setPage} />
      <main className="main-content">
        {renderPage()}
      </main>
      <footer className="footer">
        <p>Powered by TgFramework 3.1.2</p>
      </footer>
    </div>
  )
}

export default App
"""

USE_TELEGRAM_WEBAPP_TS = """import { useEffect, useState } from 'react'

declare global {
  interface Window {
    Telegram?: {
      WebApp: any
    }
  }
}

export function useTelegramWebApp() {
  const [webApp, setWebApp] = useState<any>(null)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      setWebApp(tg)
    }
  }, [])

  return webApp
}
"""

FRONTEND_README = """# Frontend - React + TypeScript

React + TypeScript фронтенд для Telegram бота с Server-Side Props.

## Установка

```bash
npm install
```

## Разработка

```bash
npm run dev  # localhost:3000
```

## Сборка

```bash
npm run build  # -> ../app/web/static/dist/
```

## Server-Side Props

Python передает данные через `__SERVER_PROPS__`:

```python
props = {'user': {...}, 'page': 'home'}
return renderer.render(props)
```

```typescript
const serverProps = (window as any).__SERVER_PROPS__;
<App {...serverProps} />
```
"""

