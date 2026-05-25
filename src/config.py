"""
Модуль конфигурации приложения.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'todo_bot')
    DB_USER = os.getenv('DB_USER', 'todo_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    @classmethod
    def get_db_url(cls):
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            print("Ошибка: BOT_TOKEN не установлен")
            return False
        if not cls.DB_PASSWORD:
            print("Ошибка: DB_PASSWORD не установлен")
            return False
        return True
