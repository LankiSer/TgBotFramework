"""
Обработчики команд и callback для бота
"""

# Импортируем bot из config
from config import bot

from tgframework import InlineKeyboardBuilder, get_user_info
from app.keyboards import register_button, menu_keyboard, yes_no_keyboard


# ========== Обработчики команд ==========

@bot.register_command("start")
async def start(update, context):
    """Обработчик команды /start"""
    user = get_user_info(context["user"])
    await bot.send_message(
        context["chat"]["id"],
        f"Привет, {user['first_name']}!\n\n"
        "Я модульный бот на TgFramework.\n"
        "Используй /help чтобы увидеть список команд.",
        reply_markup=register_button().build()
    )


@bot.register_command("help")
async def help_command(update, context):
    """Обработчик команды /help"""
    help_text = """
Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/info - Информация о пользователе
/menu - Главное меню
    """
    
    await bot.send_message(context["chat"]["id"], help_text)


@bot.register_command("info")
async def info_command(update, context):
    """Обработчик команды /info"""
    user = get_user_info(context["user"])
    chat = context["chat"]
    
    info_text = f"""
Информация о вас:

ID: {user['id']}
Имя: {user['full_name']}
Username: @{user['username'] if user['username'] else 'не указан'}
Язык: {user['language_code'] if user['language_code'] else 'не указан'}

Чат:
ID: {chat['id']}
Тип: {chat['type']}
    """
    
    await bot.send_message(context["chat"]["id"], info_text)


@bot.register_command("menu")
async def menu_command(update, context):
    """Обработчик команды /menu"""
    await bot.send_message(
        context["chat"]["id"],
        "Главное меню:",
        reply_markup=menu_keyboard().build()
    )


# ========== Обработчики callback ==========

@bot.register_callback("register_confirm")
async def register_confirm(update, context):
    """Обработчик нажатия на кнопку 'Зарегистрироваться'"""
    user_id = context["user"]["id"]
    user = get_user_info(context["user"])
    
    # Сохраняем пользователя в БД
    bot.db.add_user(
        user_id,
        username=user["username"],
        first_name=user["first_name"],
        last_name=user.get("last_name"),
        language_code=user.get("language_code"),
        is_admin=False
    )
    
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Вы успешно зарегистрированы!"
    )
    
    await bot.edit_message_text(
        context["chat"]["id"],
        context["callback_query"]["message"]["message_id"],
        f"Добро пожаловать, {user['first_name']}!\n\n"
        "Регистрация прошла успешно. Используйте /menu для навигации."
    )


@bot.register_callback("register_cancel")
async def register_cancel(update, context):
    """Обработчик нажатия на кнопку 'Отмена'"""
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Регистрация отменена"
    )
    
    await bot.edit_message_text(
        context["chat"]["id"],
        context["callback_query"]["message"]["message_id"],
        "Регистрация отменена. Используйте /start для повторной попытки."
    )


@bot.register_callback("menu_profile")
async def menu_profile(update, context):
    """Обработчик нажатия на кнопку 'Профиль'"""
    user = get_user_info(context["user"])
    user_id = context["user"]["id"]
    
    # Получаем данные из БД
    db_user = bot.db.get_user(user_id)
    
    if db_user:
        profile_text = f"""
Ваш профиль:

ID: {user['id']}
Имя: {user['full_name']}
Username: @{user['username'] if user['username'] else 'не указан'}
Язык: {user['language_code'] if user['language_code'] else 'не указан'}

Данные в БД: Зарегистрирован
        """
    else:
        profile_text = f"""
Ваш профиль:

ID: {user['id']}
Имя: {user['full_name']}
Username: @{user['username'] if user['username'] else 'не указан'}
Язык: {user['language_code'] if user['language_code'] else 'не указан'}

Данные в БД: Не зарегистрирован
Используйте /start для регистрации.
        """
    
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Профиль"
    )
    
    await bot.send_message(
        context["chat"]["id"],
        profile_text,
        reply_markup=menu_keyboard().build()
    )


@bot.register_callback("menu_help")
async def menu_help(update, context):
    """Обработчик нажатия на кнопку 'Помощь'"""
    help_text = """
Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/info - Информация о пользователе
/menu - Главное меню

Это пример модульного бота с правильной структурой:
- config.py - экземпляр бота
- app/handlers.py - обработчики команд и callback
- app/keyboards.py - клавиатуры
- main.py - точка входа
    """
    
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Помощь"
    )
    
    await bot.send_message(
        context["chat"]["id"],
        help_text,
        reply_markup=menu_keyboard().build()
    )


@bot.register_callback("menu_settings")
async def menu_settings(update, context):
    """Обработчик нажатия на кнопку 'Настройки'"""
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Настройки"
    )
    
    await bot.send_message(
        context["chat"]["id"],
        "Настройки:\n\n"
        "В данный момент настройки недоступны.\n"
        "Эта функция будет добавлена позже.",
        reply_markup=menu_keyboard().build()
    )


@bot.register_callback("button_yes")
async def button_yes(update, context):
    """Обработчик нажатия на кнопку 'Да'"""
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Вы выбрали: Да"
    )
    
    await bot.send_message(
        context["chat"]["id"],
        "Вы ответили: Да ✓"
    )


@bot.register_callback("button_no")
async def button_no(update, context):
    """Обработчик нажатия на кнопку 'Нет'"""
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Вы выбрали: Нет"
    )
    
    await bot.send_message(
        context["chat"]["id"],
        "Вы ответили: Нет ✗"
    )


# ========== Обработчики сообщений ==========

@bot.register_message_handler(
    lambda u: u.get("message", {}).get("text") and not u.get("message", {}).get("text").startswith("/")
)
async def text_handler(update, context):
    """Обработчик текстовых сообщений (не команд)"""
    text = context["text"]
    user = get_user_info(context["user"])
    
    await bot.send_message(
        context["chat"]["id"],
        f"{user['first_name']}, вы написали: {text}\n\n"
        "Я простой эхо-бот. Используйте /help для списка команд."
    )

