"""
Простой пример бота
"""

import asyncio
from tgframework import Bot, InlineKeyboardBuilder, get_user_info


# Создаём бота
bot = Bot(token="YOUR_BOT_TOKEN_HERE")


# Обработчик команды /start
@bot.register_command("start")
async def start_command(update, context):
    user = get_user_info(context["user"])
    await bot.send_message(
        context["chat"]["id"],
        f"Привет, {user['first_name']}!\n\n"
        "Я простой бот на TgFramework.\n"
        "Используй /help чтобы увидеть список команд."
    )


# Обработчик команды /help
@bot.register_command("help")
async def help_command(update, context):
    help_text = """
Доступные команды:

/start - Начать работу с ботом
/help - Показать это сообщение
/quiz - Начать квиз
/info - Информация о пользователе
    """
    
    await bot.send_message(context["chat"]["id"], help_text)


# Обработчик команды /info
@bot.register_command("info")
async def info_command(update, context):
    user = get_user_info(context["user"])
    chat = context["chat"]
    
    info_text = f"""
Информация о вас:

ID: {user['id']}
Имя: {user['full_name']}
Username: @{user['username']} (если есть)
Язык: {user.get('language_code', 'не указан')}

Информация о чате:

ID чата: {chat['id']}
Тип чата: {chat['type']}
    """
    
    await bot.send_message(context["chat"]["id"], info_text)


# Обработчик callback для кнопок
@bot.register_callback("button_")
async def button_handler(update, context):
    callback_query = context["callback_query"]
    callback_data = context["callback_data"]
    chat_id = callback_query["message"]["chat"]["id"]
    
    # Отвечаем на callback
    await bot.answer_callback_query(callback_query["id"], text="Кнопка нажата!")
    
    # Обрабатываем в зависимости от данных
    if callback_data == "button_yes":
        await bot.send_message(chat_id, "Вы ответили: Да")
    elif callback_data == "button_no":
        await bot.send_message(chat_id, "Вы ответили: Нет")


# Обработчик команды /quiz (простой пример)
@bot.register_command("quiz")
async def quiz_command(update, context):
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Да", "button_yes")
    keyboard.add_button("Нет", "button_no")
    
    await bot.send_message(
        context["chat"]["id"],
        "Вопрос: Хотите ли вы начать квиз?",
        reply_markup=keyboard.build()
    )


# Обработчик текстовых сообщений
@bot.register_message_handler(
    lambda u: u.get("message", {}).get("text") and not u.get("message", {}).get("text").startswith("/")
)
async def text_handler(update, context):
    text = context["text"]
    user = get_user_info(context["user"])
    
    await bot.send_message(
        context["chat"]["id"],
        f"{user['first_name']}, вы написали: {text}\n\n"
        "Я просто эхо-бот. Используйте /help для списка команд."
    )


if __name__ == "__main__":
    print("Запуск простого бота...")
    bot.run()

