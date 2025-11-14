"""
Пример бота с квизами
"""

import asyncio
from tgframework import (
    Bot, Quiz, QuizQuestion, InlineKeyboardBuilder, 
    get_user_info
)


bot = Bot(token="YOUR_BOT_TOKEN_HERE")


# Создаём пример квиза
def create_sample_quiz():
    """Создать пример квиза"""
    quiz = Quiz(bot.db, 0, "Тест по Python")
    
    quiz.add_question(QuizQuestion(
        question="Что такое Python?",
        options=["Змея", "Язык программирования", "Фреймворк", "Библиотека"],
        correct_answer=1,
        explanation="Python - это высокоуровневый язык программирования."
    ))
    
    quiz.add_question(QuizQuestion(
        question="Какой оператор используется для возведения в степень?",
        options=["^", "**", "pow", "exp"],
        correct_answer=1,
        explanation="Оператор ** используется для возведения в степень."
    ))
    
    quiz.add_question(QuizQuestion(
        question="Что такое список (list) в Python?",
        options=["Неизменяемая структура", "Изменяемая упорядоченная коллекция", "Словарь", "Множество"],
        correct_answer=1,
        explanation="Список - это изменяемая упорядоченная коллекция элементов."
    ))
    
    return quiz


@bot.register_command("start")
async def start_command(update, context):
    user = get_user_info(context["user"])
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Начать квиз", "quiz_start")
    keyboard.add_button("Правила", "quiz_rules")
    
    await bot.send_message(
        context["chat"]["id"],
        f"Привет, {user['first_name']}!\n\n"
        "Добро пожаловать в бота с квизами!\n"
        "Выберите действие:",
        reply_markup=keyboard.build()
    )


@bot.register_command("quiz")
async def quiz_start_command(update, context):
    await start_quiz(update, context)


async def start_quiz(update, context):
    """Начать новый квиз"""
    user_id = context["user"]["id"]
    
    # Проверяем, есть ли активный квиз
    active_quiz = Quiz.get_user_active_quiz(bot.db, user_id)
    if active_quiz:
        await bot.send_message(
            context["chat"]["id"],
            "У вас уже есть активный квиз! Используйте /continue для продолжения."
        )
        return
    
    # Создаём новый квиз
    quiz = create_sample_quiz()
    quiz.user_id = user_id
    quiz.save()
    
    # Показываем первый вопрос
    await show_question(update, context, quiz)


async def show_question(update, context, quiz: Quiz):
    """Показать вопрос квиза"""
    question = quiz.get_current_question()
    if not question:
        await finish_quiz(update, context, quiz)
        return
    
    keyboard = InlineKeyboardBuilder()
    for i, option in enumerate(question.options):
        keyboard.add_button(option, f"quiz_answer_{quiz.quiz_id}_{i}")
        keyboard.row()
    
    question_text = f"Вопрос {quiz.current_question + 1} из {len(quiz.questions)}\n\n"
    question_text += question.question
    
    if "callback_query" in context:
        await bot.edit_message_text(
            context["chat"]["id"],
            context["callback_query"]["message"]["message_id"],
            question_text,
            reply_markup=keyboard.build()
        )
    else:
        await bot.send_message(
            context["chat"]["id"],
            question_text,
            reply_markup=keyboard.build()
        )


@bot.register_callback("quiz_start")
async def quiz_start_callback(update, context):
    await bot.answer_callback_query(context["callback_query"]["id"])
    await start_quiz(update, context)


@bot.register_callback("quiz_answer_")
async def quiz_answer_callback(update, context):
    callback_data = context["callback_data"]
    parts = callback_data.split("_")
    quiz_id = int(parts[2])
    answer_index = int(parts[3])
    
    user_id = context["user"]["id"]
    
    # Загружаем квиз
    quiz = Quiz(bot.db, user_id)
    quiz.load(quiz_id)
    
    if quiz.user_id != user_id:
        await bot.answer_callback_query(
            context["callback_query"]["id"],
            text="Этот квиз не ваш!",
            show_alert=True
        )
        return
    
    # Проверяем ответ
    is_correct = quiz.answer(answer_index)
    current_question = quiz.get_current_question()
    
    # Показываем результат
    if is_correct:
        result_text = "Правильно!\n\n"
    else:
        result_text = f"Неправильно. Правильный ответ: {current_question.options[current_question.correct_answer]}\n\n"
    
    if current_question.explanation:
        result_text += f"{current_question.explanation}\n\n"
    
    result_text += f"Текущий счёт: {quiz.score}/{len(quiz.questions)}"
    
    await bot.answer_callback_query(
        context["callback_query"]["id"],
        text="Правильно!" if is_correct else "Неправильно!"
    )
    
    # Ждём немного и показываем следующий вопрос
    await asyncio.sleep(1)
    
    # Переходим к следующему вопросу
    next_question = quiz.next_question()
    
    if next_question:
        await show_question(update, context, quiz)
    else:
        await finish_quiz(update, context, quiz)


async def finish_quiz(update, context, quiz: Quiz):
    """Завершить квиз и показать результаты"""
    results = quiz.get_results()
    quiz.finish()
    
    keyboard = InlineKeyboardBuilder()
    keyboard.add_button("Начать заново", "quiz_start")
    
    results_text = "Квиз завершён!\n\n"
    results_text += f"Результаты:\n"
    results_text += f"Правильных ответов: {results['correct']}/{results['total']}\n"
    results_text += f"Процент: {results['percentage']}%\n\n"
    
    if results['percentage'] >= 80:
        results_text += "Отличный результат!"
    elif results['percentage'] >= 60:
        results_text += "Хороший результат!"
    else:
        results_text += "Попробуйте ещё раз!"
    
    if "callback_query" in context:
        await bot.edit_message_text(
            context["chat"]["id"],
            context["callback_query"]["message"]["message_id"],
            results_text,
            reply_markup=keyboard.build()
        )
    else:
        await bot.send_message(
            context["chat"]["id"],
            results_text,
            reply_markup=keyboard.build()
        )


@bot.register_callback("quiz_rules")
async def quiz_rules_callback(update, context):
    await bot.answer_callback_query(context["callback_query"]["id"])
    
    rules_text = """
Правила квиза:

1. Квиз состоит из нескольких вопросов
2. На каждый вопрос нужно выбрать один правильный ответ
3. После ответа вы увидите результат и объяснение
4. В конце квиза вы увидите свой итоговый счёт

Удачи!
    """
    
    await bot.send_message(
        context["chat"]["id"],
        rules_text
    )


@bot.register_command("continue")
async def continue_quiz_command(update, context):
    user_id = context["user"]["id"]
    active_quiz = Quiz.get_user_active_quiz(bot.db, user_id)
    
    if active_quiz:
        await show_question(update, context, active_quiz)
    else:
        await bot.send_message(
            context["chat"]["id"],
            "У вас нет активного квиза. Используйте /quiz для начала нового квиза."
        )


if __name__ == "__main__":
    print("Запуск бота с квизами...")
    bot.run()

