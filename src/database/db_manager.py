"""
Менеджер базы данных для Todo List.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from src.config import Config
from src.database.models import User, Task


class DatabaseManager:
    """Менеджер подключения к БД."""
    
    def __init__(self):
        self.conn = None
    
    def connect(self):
        """Устанавливает соединение."""
        self.conn = psycopg2.connect(Config.get_db_url())
        print("Подключение к БД установлено")
    
    def close(self):
        """Закрывает соединение."""
        if self.conn:
            self.conn.close()
    
    def create_user(self, user_id: int, username: Optional[str],
                    first_name: Optional[str], last_name: Optional[str]) -> bool:
        """Создает пользователя."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (user_id, username, first_name, last_name)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, username, first_name, last_name))
            self.conn.commit()
            return cur.rowcount > 0
    
    def add_task(self, user_id: int, title: str) -> Optional[int]:
        """Добавляет новую задачу."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tasks (user_id, title)
                VALUES (%s, %s)
                RETURNING id
            """, (user_id, title))
            self.conn.commit()
            return cur.fetchone()[0]
    
    def get_user_tasks(self, user_id: int) -> List[Task]:
        """Получает все задачи пользователя."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM tasks 
                WHERE user_id = %s
                ORDER BY 
                    CASE WHEN status = 'pending' THEN 0 ELSE 1 END,
                    created_at ASC
            """, (user_id,))
            rows = cur.fetchall()
            return [Task(**row) for row in rows]
    
    def complete_task(self, task_id: int, user_id: int) -> bool:
        """Отмечает задачу как выполненную."""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE tasks 
                SET status = 'completed', updated_at = NOW()
                WHERE id = %s AND user_id = %s AND status = 'pending'
            """, (task_id, user_id))
            self.conn.commit()
            return cur.rowcount > 0
    
    def delete_task(self, task_id: int, user_id: int) -> bool:
        """Удаляет задачу."""
        with self.conn.cursor() as cur:
            cur.execute("""
                DELETE FROM tasks
                WHERE id = %s AND user_id = %s
            """, (task_id, user_id))
            self.conn.commit()
            return cur.rowcount > 0
    
    def get_task_count(self, user_id: int) -> dict:
        """Получает статистику по задачам."""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
                FROM tasks
                WHERE user_id = %s
            """, (user_id,))
            row = cur.fetchone()
            return {
                'total': row['total'] or 0,
                'pending': row['pending'] or 0,
                'completed': row['completed'] or 0
            }
