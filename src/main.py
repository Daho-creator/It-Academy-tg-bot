"""
Главный файл для запуска Todo List бота.
"""

from bot import TodoBot


def main():
    """Запуск приложения."""
    bot = TodoBot()
    bot.run()


if __name__ == '__main__':
    main()
