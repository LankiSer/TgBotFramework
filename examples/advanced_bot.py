"""
Продвинутый пример бота с использованием новых возможностей TgFramework 2.0
Демонстрирует: фильтры, FSM, pagination, error handling, rate limiting
"""

from tgframework import (
    Bot, Filters, FSMState, StatesGroup, FSMContext, state,
    PaginationKeyboard
)


class MyStates(StatesGroup):
    """Группа состояний для FSM"""
    waiting_for_name = FSMState()
    waiting_for_age = FSMState()
    waiting_for_city = FSMState()


bot = Bot(token="YOUR_BOT_TOKEN_HERE")


# Обработчик ошибок
@bot.register_error_handler
async def error_handler(error, context):
    """Глобальный обработчик ошибок"""
    print(f"Произошла ошибка: {error}")
    if "update" in context:
        update = context["update"]
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            try:
                await bot.send_message(
                    chat_id,
                    "Произошла ошибка при обработке вашего запроса. Попробуйте позже."
                )
            except:
                pass


# Обработчик команды /start с началом FSM
@bot.register_command("start")
async def start_command(update, context):
    chat_id = context["chat"]["id"]
    user_id = context["user"]["id"]
    
    fsm = FSMContext(bot.state_machine, user_id, chat_id)
    await fsm.set_state(MyStates.waiting_for_name)
    
    await bot.send_message(
        chat_id,
        "Привет! Давайте познакомимся.\nВведите ваше имя:"
    )


# Обработчик состояния waiting_for_name
@state(MyStates.waiting_for_name)
async def handle_name(update, context):
    chat_id = context["chat"]["id"]
    user_id = context["user"]["id"]
    text = context["text"]
    
    fsm = FSMContext(bot.state_machine, user_id, chat_id)
    await fsm.update_data(name=text)
    await fsm.set_state(MyStates.waiting_for_age)
    
    await bot.send_message(
        chat_id,
        f"Приятно познакомиться, {text}!\nТеперь введите ваш возраст:"
    )


# Обработчик состояния waiting_for_age
@state(MyStates.waiting_for_age)
async def handle_age(update, context):
    chat_id = context["chat"]["id"]
    user_id = context["user"]["id"]
    text = context["text"]
    
    try:
        age = int(text)
        fsm = FSMContext(bot.state_machine, user_id, chat_id)
        await fsm.update_data(age=age)
        await fsm.set_state(MyStates.waiting_for_city)
        
        await bot.send_message(
            chat_id,
            f"Отлично! Вам {age} лет.\nТеперь введите ваш город:"
        )
    except ValueError:
        await bot.send_message(
            chat_id,
            "Пожалуйста, введите корректный возраст (число):"
        )


# Обработчик состояния waiting_for_city
@state(MyStates.waiting_for_city)
async def handle_city(update, context):
    chat_id = context["chat"]["id"]
    user_id = context["user"]["id"]
    text = context["text"]
    
    fsm = FSMContext(bot.state_machine, user_id, chat_id)
    data = await fsm.get_data()
    
    await fsm.finish()  # Завершаем FSM
    
    name = data.get("name", "Неизвестно")
    age = data.get("age", "Неизвестно")
    city = text
    
    await bot.send_message(
        chat_id,
        f"Спасибо за информацию!\n\n"
        f"Имя: {name}\n"
        f"Возраст: {age}\n"
        f"Город: {city}\n\n"
        f"Регистрация завершена!"
    )


# Обработчик с фильтром для фото
@bot.register_message_handler(filters=Filters.Photo())
async def photo_handler(update, context):
    chat_id = context["chat"]["id"]
    await bot.send_message(
        chat_id,
        "Получено фото! Спасибо за отправку."
    )


# Обработчик с фильтром для документов
@bot.register_message_handler(filters=Filters.Document())
async def document_handler(update, context):
    chat_id = context["chat"]["id"]
    document = context["message"].get("document", {})
    file_name = document.get("file_name", "неизвестный файл")
    
    await bot.send_message(
        chat_id,
        f"Получен документ: {file_name}"
    )


# Обработчик с комбинацией фильтров
@bot.register_message_handler(filters=Filters.Text() & Filters.PrivateChat())
async def private_text_handler(update, context):
    chat_id = context["chat"]["id"]
    text = context["text"]
    
    # Проверяем, не в FSM ли мы
    user_id = context["user"]["id"]
    current_state = bot.state_machine.get_state(user_id)
    
    if not current_state:
        await bot.send_message(
            chat_id,
            f"Вы написали в приватный чат: {text}\n"
            "Используйте /start для регистрации."
        )


# Пример с pagination
@bot.register_command("list")
async def list_command(update, context):
    chat_id = context["chat"]["id"]
    
    # Примерный список элементов
    items = [f"Элемент {i+1}" for i in range(25)]
    
    pagination = PaginationKeyboard(
        items=items,
        items_per_page=5,
        callback_prefix="list_",
        item_formatter=lambda x: x
    )
    
    await bot.send_message(
        chat_id,
        "Список элементов (используйте кнопки для навигации):",
        reply_markup=pagination.build(0)
    )


# Обработчик callback для pagination
@bot.register_callback("list_page_")
async def pagination_callback(update, context):
    callback_data = context["callback_data"]
    chat_id = context["callback_query"]["message"]["chat"]["id"]
    message_id = context["callback_query"]["message"]["message_id"]
    
    if callback_data == "list_current":
        await bot.answer_callback_query(context["callback_query"]["id"])
        return
    
    # Извлекаем номер страницы
    try:
        page_num = int(callback_data.split("_")[-1])
    except:
        page_num = 0
    
    # Создаем ту же пагинацию
    items = [f"Элемент {i+1}" for i in range(25)]
    pagination = PaginationKeyboard(
        items=items,
        items_per_page=5,
        callback_prefix="list_",
        item_formatter=lambda x: x
    )
    
    await bot.answer_callback_query(context["callback_query"]["id"])
    await bot.edit_message_text(
        chat_id,
        message_id,
        "Список элементов (используйте кнопки для навигации):",
        reply_markup=pagination.build(page_num)
    )


# Обработчик выбора элемента из списка
@bot.register_callback("list_item_")
async def list_item_callback(update, context):
    callback_data = context["callback_data"]
    
    try:
        item_index = int(callback_data.split("_")[-1])
        items = [f"Элемент {i+1}" for i in range(25)]
        
        if 0 <= item_index < len(items):
            selected_item = items[item_index]
            
            await bot.answer_callback_query(
                context["callback_query"]["id"],
                text=f"Выбран: {selected_item}"
            )
            
            await bot.send_message(
                context["callback_query"]["message"]["chat"]["id"],
                f"Вы выбрали: {selected_item}"
            )
    except:
        await bot.answer_callback_query(
            context["callback_query"]["id"],
            text="Ошибка при обработке выбора"
        )


# Регистрация FSM обработчиков
# Обработчики с декоратором @state автоматически вызываются через bot.state_handlers
for handler in [handle_name, handle_age, handle_city]:
    if hasattr(handler, "_is_state_handler") and hasattr(handler, "_state"):
        state_str = str(handler._state)
        bot.state_handlers.setdefault(state_str, []).append(handler)


if __name__ == "__main__":
    print("Запуск продвинутого бота...")
    print("Возможности:")
    print("- FSM (конечный автомат состояний)")
    print("- Фильтры для сообщений")
    print("- Pagination для списков")
    print("- Обработка ошибок")
    print("- Rate limiting")
    bot.run()
