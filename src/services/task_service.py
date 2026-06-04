"""
Сервис для работы с задачами.
"""

from typing import Tuple
from src.database.db_manager import DatabaseManager


class TaskService:
    """Сервис управления задачами."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    async def add_task(self, user_id: int, title: str) -> Tuple[bool, str]:
        if not title or len(title.strip()) == 0:
            return False, "❌ Название задачи не может быть пустым"
        
        if len(title) > 500:
            return False, "❌ Название не должно превышать 500 символов"
        
        task_id = self.db.add_task(user_id, title.strip())
        
        if task_id:
            return True, f"✅ Задача добавлена!\n\n📝 {title}"
        return False, "❌ Ошибка при добавлении задачи"
    
    async def list_tasks(self, user_id: int) -> str:
        tasks = self.db.get_user_tasks(user_id)
        stats = self.db.get_task_count(user_id)
        
        if not tasks:
            return "📭 У вас пока нет задач\n\nИспользуйте /add чтобы добавить задачу"
        
        result = f"📋 *Ваш список дел*\n"
        result += f"📊 Всего: {stats['total']} | ⭕️ Активных: {stats['pending']} | ✅ Выполнено: {stats['completed']}\n\n"
        
        pending_tasks = [t for t in tasks if not t.is_completed()]
        completed_tasks = [t for t in tasks if t.is_completed()]
        
        if pending_tasks:
            result += "📌 *Активные задачи:*\n"
            for i, task in enumerate(pending_tasks, 1):
                result += f"{i}. {task.title}\n"
            result += "\n"
        
        if completed_tasks:
            result += "✅ *Выполненные задачи:*\n"
            for i, task in enumerate(completed_tasks, 1):
                result += f"{i}. ~~{task.title}~~\n"
        
        result += "\n💡 *Команды:*\n"
        result += "➡️ /complete <номер> - отметить выполненной\n"
        result += "➡️ /delete <номер> - удалить задачу"
        
        return result
    
    async def complete_task(self, user_id: int, index_str: str) -> Tuple[bool, str]:
        try:
            index = int(index_str) - 1
            tasks = self.db.get_user_tasks(user_id)
            pending_tasks = [t for t in tasks if not t.is_completed()]
            
            if index < 0 or index >= len(pending_tasks):
                return False, "❌ Неверный номер задачи"
            
            task = pending_tasks[index]
            success = self.db.complete_task(task.id, user_id)
            
            if success:
                return True, f"✅ Задача выполнена!\n\n📝 {task.title}"
            return False, "❌ Ошибка при выполнении задачи"
        except ValueError:
            return False, "❌ Введите номер задачи"
    
    async def delete_task(self, user_id: int, index_str: str) -> Tuple[bool, str]:
        try:
            index = int(index_str) - 1
            tasks = self.db.get_user_tasks(user_id)
            
            if index < 0 or index >= len(tasks):
                return False, "❌ Неверный номер задачи"
            
            task = tasks[index]
            success = self.db.delete_task(task.id, user_id)
            
            if success:
                return True, f"🗑 Задача удалена!\n\n📝 {task.title}"
            return False, "❌ Ошибка при удалении задачи"
        except ValueError:
            return False, "❌ Введите номер задачи"
