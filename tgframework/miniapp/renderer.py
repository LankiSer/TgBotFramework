"""
Рендеринг React/Next.js с серверными переменными
"""

import json
from typing import Dict, Any
from pathlib import Path


class ReactRenderer:
    """Рендерер для React приложений с серверными переменными"""
    
    def __init__(self, template_dir: str = "web/templates"):
        self.template_dir = Path(template_dir)
    
    def render(self, template_name: str, context: Dict[str, Any] = None) -> str:
        """
        Рендерить React приложение с серверными переменными
        
        Args:
            template_name: Имя шаблона
            context: Контекст с переменными для передачи в React
            
        Returns:
            HTML с внедренными переменными
        """
        if context is None:
            context = {}
        
        template_path = self.template_dir / template_name
        
        if not template_path.exists():
            # Создаем дефолтный шаблон
            html = self._create_default_template()
        else:
            html = template_path.read_text()
        
        # Внедряем серверные переменные
        server_data = json.dumps(context, ensure_ascii=False)
        
        # Добавляем скрипт с данными
        script = f"""
    <script id="__SERVER_DATA__" type="application/json">
        {server_data}
    </script>
        """
        
        # Вставляем перед закрывающим </body>
        if '</body>' in html:
            html = html.replace('</body>', f'{script}</body>')
        else:
            html += script
        
        return html
    
    def _create_default_template(self) -> str:
        """Создать дефолтный React шаблон"""
        return """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Mini App</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--tg-theme-bg-color, #ffffff);
            color: var(--tg-theme-text-color, #000000);
        }
        #root {
            padding: 20px;
        }
    </style>
</head>
<body>
    <div id="root"></div>
    
    <script type="text/babel">
        // Получаем серверные данные
        const getServerData = () => {
            const script = document.getElementById('__SERVER_DATA__');
            return script ? JSON.parse(script.textContent) : {};
        };
        
        const App = () => {
            const [data, setData] = React.useState(getServerData());
            const [count, setCount] = React.useState(0);
            
            React.useEffect(() => {
                // Инициализация Telegram WebApp
                if (window.Telegram?.WebApp) {
                    const tg = window.Telegram.WebApp;
                    tg.ready();
                    tg.expand();
                    
                    // Настройка кнопки
                    tg.MainButton.setText('Отправить');
                    tg.MainButton.onClick(() => {
                        tg.sendData(JSON.stringify({ count, ...data }));
                    });
                    tg.MainButton.show();
                }
            }, [count, data]);
            
            return (
                <div>
                    <h1>Telegram Mini App</h1>
                    <p>Серверные данные:</p>
                    <pre>{JSON.stringify(data, null, 2)}</pre>
                    
                    <h2>Счетчик: {count}</h2>
                    <button onClick={() => setCount(count + 1)}>
                        Увеличить
                    </button>
                </div>
            );
        };
        
        ReactDOM.render(<App />, document.getElementById('root'));
    </script>
</body>
</html>
"""


class NextJSRenderer:
    """Рендерер для Next.js приложений"""
    
    def __init__(self, nextjs_url: str = "http://localhost:3000"):
        self.nextjs_url = nextjs_url
    
    async def render(self, path: str, context: Dict[str, Any] = None) -> str:
        """
        Получить рендер от Next.js сервера с серверными переменными
        
        Args:
            path: Путь к странице
            context: Контекст для передачи в Next.js
            
        Returns:
            HTML от Next.js
        """
        import aiohttp
        
        if context is None:
            context = {}
        
        url = f"{self.nextjs_url}{path}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={'serverData': json.dumps(context)}) as response:
                html = await response.text()
                return html
    
    def get_props_script(self, props: Dict[str, Any]) -> str:
        """
        Создать скрипт с серверными пропсами для Next.js
        
        Args:
            props: Пропсы для передачи
            
        Returns:
            Скрипт с данными
        """
        return f"""
<script id="__NEXT_DATA__" type="application/json">
{json.dumps({"props": {"pageProps": props}}, ensure_ascii=False)}
</script>
        """


class ServerSidePropsInjector:
    """Инжектор серверных пропсов в React/Next.js"""
    
    @staticmethod
    def inject_props(html: str, props: Dict[str, Any]) -> str:
        """
        Внедрить серверные пропсы в HTML
        
        Args:
            html: HTML страницы
            props: Пропсы для внедрения
            
        Returns:
            HTML с внедренными пропсами
        """
        props_json = json.dumps(props, ensure_ascii=False)
        
        script = f"""
<script>
    window.__SERVER_PROPS__ = {props_json};
</script>
        """
        
        if '</head>' in html:
            html = html.replace('</head>', f'{script}</head>')
        elif '<body>' in html:
            html = html.replace('<body>', f'<body>{script}')
        else:
            html = script + html
        
        return html
    
    @staticmethod
    def create_props_provider(props: Dict[str, Any]) -> str:
        """
        Создать React Provider для серверных пропсов
        
        Args:
            props: Пропсы
            
        Returns:
            JavaScript код для провайдера
        """
        return f"""
const ServerPropsContext = React.createContext({json.dumps(props)});

export const useServerProps = () => {{
    return React.useContext(ServerPropsContext);
}};

export const ServerPropsProvider = ({{ children }}) => {{
    const props = window.__SERVER_PROPS__ || {json.dumps(props)};
    return (
        <ServerPropsContext.Provider value={{props}}>
            {{children}}
        </ServerPropsContext.Provider>
    );
}};
        """

