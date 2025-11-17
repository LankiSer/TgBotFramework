"""
Пример бота с регистрацией и админкой
"""

import asyncio
from tgframework import (
    Bot, InlineKeyboardBuilder, get_user_info
)


bot = Bot(token="YOUR_BOT_TOKEN_HERE")

# ID первого администратора (установить вручную при первом запуске)
FIRST_ADMIN_ID = 123456789  # Замените на ваш Telegram ID


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return bot.db.is_admin(user_id)


async def require_admin(update, context, handler):
    """Декоратор для проверки прав администратора"""
    user_id = context["user"]["id"]
    if not is_admin(user_id):
        await bot.send_message(
            context["chat"]["id"],
            "У вас нет прав для выполнения этой команды."
        )
        return
    await handler(update, context)


@bot.register_command("start")
async def start_command(update, context):
    user_id = context["user"]["id"]
    user = get_user_info(context["user"])
    
    # Проверяем, зарегистрирован ли пользователь
    db_user = bot.db.get_user(user_id)
    
    if not db_user:
        # Первый пользователь автоматически становится админом
        if user_id == FIRST_ADMIN_ID:
            bot.db.add_user(
                user_id,
                user["username"],
                user["first_name"],
                user["last_name"],
                user.get("language_code"),
                is_admin=True
            )
            await bot.send_message(
                context["chat"]["id"],
                f"Привет, {user['first_name']}! Вы зарегистрированы как администратор.\n\n"
                "Используйте /help для списка команд."
            )
        else:
            keyboard = InlineKeyboardBuilder()
            keyboard.add_button("Зарегистрироваться", "register_confirm")
            
            await bot.send_message(
                context["chat"]["id"],
                f"Привет, {user['first_name']}!\n\n"
                "Для использования бота необходимо зарегистрироваться.",
                reply_markup=keyboard.build()
            )
    else:
        # Пользователь уже зарегистрирован
        status = "администратор" if is_admin(user_id) else "пользователь"
        await bot.send_message(
            context["chat"]["id"],
            f"Привет, {user['first_name']}!\n\n"
            f"Ваш статус: {status}\n\n"
            "Используйте /help для списка команд."
        )


@bot.register_callback("register_confirm")
async def register_callback(update, context):
    user_id = context["user"]["id"]
    user = get_user_info(context["user"])
    
    # Проверяем, не зарегистрирован ли уже
    db_user = bot.db.get_user(user_id)
    if db_user:
        await bot.answer_callback_query(
            context["callback_query"]["id"],
            text="Вы уже зарегистрированы!"
        )
        return
    
    # Регистрируем пользователя
    bot.db.add_user(
        user_id,
        user["username"],
        user["first_name"],
        user["last_name"],
        user.get("language_code"),
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
        "Регистрация прошла успешно. Используйте /help для списка команд."
    )


@bot.register_command("help")
async def help_command(update, context):
    user_id = context["user"]["id"]
    
    help_text = "Доступные команды:\n\n"
    help_text += "/start - Начать работу с ботом\n"
    help_text += "/profile - Мой профиль\n"
    help_text += "/help - Показать это сообщение\n\n"
    
    if is_admin(user_id):
        help_text += "Команды администратора:\n"
        help_text += "/admin_stats - Статистика бота\n"
        help_text += "/admin_users - Список пользователей\n"
        help_text += "/admin_set <user_id> <0/1> - Установить статус администратора\n"
        help_text += "/admin_broadcast <текст> - Отправить сообщение всем пользователям\n"
    
    await bot.send_message(context["chat"]["id"], help_text)


@bot.register_command("profile")
async def profile_command(update, context):
    user_id = context["user"]["id"]
    user = get_user_info(context["user"])
    db_user = bot.db.get_user(user_id)
    
    if not db_user:
        await bot.send_message(
            context["chat"]["id"],
            "Вы не зарегистрированы. Используйте /start для регистрации."
        )
        return
    
    status = "Администратор" if is_admin(user_id) else "Пользователь"
    created_at = db_user.get("created_at", "неизвестно")
    
    profile_text = f"Ваш профиль:\n\n"
    profile_text += f"ID: {user_id}\n"
    profile_text += f"Имя: {user['full_name']}\n"
    profile_text += f"Username: @{user['username']}\n" if user['username'] else ""
    profile_text += f"Статус: {status}\n"
    profile_text += f"Зарегистрирован: {created_at}\n"
    
    await bot.send_message(context["chat"]["id"], profile_text)


# Админские команды

@bot.register_command("admin_stats")
async def admin_stats_command(update, context):
    async def handler(update, context):
        user_count = bot.db.get_user_count()
        admins = bot.db.get_all_admins()
        admin_count = len(admins)
        
        stats_text = "Статистика бота:\n\n"
        stats_text += f"Всего пользователей: {user_count}\n"
        stats_text += f"Администраторов: {admin_count}\n"
        stats_text += f"Обычных пользователей: {user_count - admin_count}\n"
        
        await bot.send_message(context["chat"]["id"], stats_text)
    
    await require_admin(update, context, handler)


@bot.register_command("admin_users")
async def admin_users_command(update, context):
    async def handler(update, context):
        users = bot.db.get_all_users(limit=20)
        
        if not users:
            await bot.send_message(context["chat"]["id"], "Пользователи не найдены.")
            return
        
        users_text = "Список пользователей (последние 20):\n\n"
        for user in users:
            status = "Админ" if user.get("is_admin", 0) else "Пользователь"
            name = user.get("first_name", "Неизвестно")
            user_id = user.get("user_id")
            users_text += f"{name} (ID: {user_id}) - {status}\n"
        
        await bot.send_message(context["chat"]["id"], users_text)
    
    await require_admin(update, context, handler)


@bot.register_command("admin_set")
async def admin_set_command(update, context):
    async def handler(update, context):
        args = context.get("args", "")
        
        if not args:
            await bot.send_message(
                context["chat"]["id"],
                "Использование: /admin_set <user_id> <0/1>\n"
                "0 - убрать права администратора\n"
                "1 - дать права администратора"
            )
            return
        
        parts = args.split()
        if len(parts) < 2:
            await bot.send_message(
                context["chat"]["id"],
                "Неверный формат. Используйте: /admin_set <user_id> <0/1>"
            )
            return
        
        try:
            target_user_id = int(parts[0])
            is_admin_value = int(parts[1]) == 1
            
            target_user = bot.db.get_user(target_user_id)
            if not target_user:
                await bot.send_message(
                    context["chat"]["id"],
                    f"Пользователь с ID {target_user_id} не найден."
                )
                return
            
            bot.db.set_admin(target_user_id, is_admin_value)
            
            target_name = target_user.get("first_name", "Пользователь")
            status_text = "назначен администратором" if is_admin_value else "лишен прав администратора"
            
            await bot.send_message(
                context["chat"]["id"],
                f"Пользователь {target_name} (ID: {target_user_id}) {status_text}."
            )
        except ValueError:
            await bot.send_message(
                context["chat"]["id"],
                "Ошибка: неверный формат ID или значения."
            )
    
    await require_admin(update, context, handler)


@bot.register_command("admin_broadcast")
async def admin_broadcast_command(update, context):
    async def handler(update, context):
        args = context.get("args", "")
        
        if not args:
            await bot.send_message(
                context["chat"]["id"],
                "Использование: /admin_broadcast <текст сообщения>"
            )
            return
        
        users = bot.db.get_all_users()
        sent_count = 0
        failed_count = 0
        
        await bot.send_message(
            context["chat"]["id"],
            f"Отправка сообщения {len(users)} пользователям..."
        )
        
        for user in users:
            try:
                user_id = user.get("user_id")
                await bot.send_message(user_id, f"Рассылка от администратора:\n\n{args}")
                sent_count += 1
                await asyncio.sleep(0.05)  # Небольшая задержка для избежания rate limit
            except Exception as e:
                failed_count += 1
                print(f"Ошибка отправки пользователю {user_id}: {e}")
        
        await bot.send_message(
            context["chat"]["id"],
            f"Рассылка завершена:\n"
            f"Отправлено: {sent_count}\n"
            f"Ошибок: {failed_count}"
        )
    
    await require_admin(update, context, handler)


if __name__ == "__main__":
    print("Запуск бота с регистрацией и админкой...")
    print(f"Первый администратор: {FIRST_ADMIN_ID}")
    print("Не забудьте установить правильный FIRST_ADMIN_ID в коде!")
    bot.run()

