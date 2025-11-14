"""
Система квизов
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class QuizQuestion:
    """Вопрос для квиза"""
    question: str
    options: List[str]
    correct_answer: int  # Индекс правильного ответа
    explanation: Optional[str] = None


class Quiz:
    """Класс для работы с квизами"""
    
    def __init__(self, db, user_id: int, title: str = "Квиз"):
        """
        Инициализация квиза
        
        Args:
            db: Экземпляр базы данных
            user_id: ID пользователя
            title: Название квиза
        """
        self.db = db
        self.user_id = user_id
        self.title = title
        self.questions: List[QuizQuestion] = []
        self.current_question = 0
        self.score = 0
        self.quiz_id: Optional[int] = None
    
    def add_question(self, question: QuizQuestion):
        """
        Добавить вопрос в квиз
        
        Args:
            question: Вопрос для добавления
        """
        self.questions.append(question)
    
    def add_questions(self, questions: List[QuizQuestion]):
        """
        Добавить несколько вопросов
        
        Args:
            questions: Список вопросов
        """
        self.questions.extend(questions)
    
    def save(self):
        """Сохранить квиз в базу данных"""
        questions_json = json.dumps([asdict(q) for q in self.questions])
        
        if self.quiz_id:
            # Обновить существующий квиз
            self.db.execute("""
                UPDATE quizzes 
                SET questions = ?, current_question = ?, score = ?
                WHERE quiz_id = ?
            """, (questions_json, self.current_question, self.score, self.quiz_id))
        else:
            # Создать новый квиз
            cursor = self.db.execute("""
                INSERT INTO quizzes (user_id, title, questions, current_question, score, status)
                VALUES (?, ?, ?, ?, ?, 'active')
            """, (self.user_id, self.title, questions_json, self.current_question, self.score))
            self.quiz_id = cursor.lastrowid
        
        return self.quiz_id
    
    def load(self, quiz_id: int):
        """
        Загрузить квиз из базы данных
        
        Args:
            quiz_id: ID квиза
        """
        quiz_data = self.db.fetchone("SELECT * FROM quizzes WHERE quiz_id = ?", (quiz_id,))
        if quiz_data:
            self.quiz_id = quiz_data["quiz_id"]
            self.user_id = quiz_data["user_id"]
            self.title = quiz_data["title"]
            self.current_question = quiz_data["current_question"]
            self.score = quiz_data["score"]
            
            if quiz_data["questions"]:
                questions_data = json.loads(quiz_data["questions"])
                self.questions = [QuizQuestion(**q) for q in questions_data]
    
    def get_current_question(self) -> Optional[QuizQuestion]:
        """Получить текущий вопрос"""
        if 0 <= self.current_question < len(self.questions):
            return self.questions[self.current_question]
        return None
    
    def answer(self, answer_index: int) -> bool:
        """
        Ответить на текущий вопрос
        
        Args:
            answer_index: Индекс выбранного ответа
            
        Returns:
            True если ответ правильный, False если неправильный
        """
        question = self.get_current_question()
        if question and answer_index == question.correct_answer:
            self.score += 1
            return True
        return False
    
    def next_question(self) -> Optional[QuizQuestion]:
        """Перейти к следующему вопросу"""
        self.current_question += 1
        self.save()
        return self.get_current_question()
    
    def is_finished(self) -> bool:
        """Проверить, завершён ли квиз"""
        return self.current_question >= len(self.questions)
    
    def get_results(self) -> Dict[str, Any]:
        """
        Получить результаты квиза
        
        Returns:
            Словарь с результатами
        """
        total = len(self.questions)
        percentage = (self.score / total * 100) if total > 0 else 0
        
        return {
            "score": self.score,
            "total": total,
            "percentage": round(percentage, 2),
            "correct": self.score,
            "incorrect": total - self.score
        }
    
    def finish(self):
        """Завершить квиз"""
        self.db.execute("""
            UPDATE quizzes 
            SET status = 'finished' 
            WHERE quiz_id = ?
        """, (self.quiz_id,))
    
    @staticmethod
    def get_user_active_quiz(db, user_id: int) -> Optional['Quiz']:
        """
        Получить активный квиз пользователя
        
        Args:
            db: Экземпляр базы данных
            user_id: ID пользователя
            
        Returns:
            Активный квиз или None
        """
        quiz_data = db.fetchone("""
            SELECT * FROM quizzes 
            WHERE user_id = ? AND status = 'active' 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id,))
        
        if quiz_data:
            quiz = Quiz(db, user_id, quiz_data["title"])
            quiz.load(quiz_data["quiz_id"])
            return quiz
        return None

