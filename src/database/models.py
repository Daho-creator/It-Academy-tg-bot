"""
Модели данных для Todo List.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: datetime


@dataclass
class Task:
    id: Optional[int]
    user_id: int
    title: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    def is_completed(self) -> bool:
        """Проверяет, выполнена ли задача."""
        return self.status == 'completed'
    
    def get_status_emoji(self) -> str:
        """Возвращает эмодзи для статуса."""
        return "✅" if self.is_completed() else "⭕️"
