"""
Сервис для статистики и напоминаний.
"""

from datetime import datetime
from src.database.db_manager import DatabaseManager


class NotificationService:
    """Сервис для статистики."""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_daily_stats(self, user_id: int) -> str:
        """Получает дневную статистику."""
        stats = self.db.get_task_count(user_id)
        
        result = f"📊 *Статистика на {datetime.now().strftime('%d.%m.%Y')}*\n\n"
        result += f"📋 Всего задач: {stats['total']}\n"
        result += f"⭕️ Активных: {stats['pending']}\n"
        result += f"✅ Выполнено: {stats['completed']}\n"
        
        if stats['total'] > 0:
            completion_rate = (stats['completed'] / stats['total']) * 100
            result += f"\n📈 Прогресс: {completion_rate:.1f}%"
            if completion_rate == 100:
                result += "\n\n🎉 Поздравляю! Все задачи выполнены!"
        
        return result
