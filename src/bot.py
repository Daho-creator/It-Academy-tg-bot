import sys
import os
sys.path.insert(0, '/Users/daho/Akademy_Project/It-Academy-tg-bot')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters, ContextTypes
)
from config import Config
from database.db_manager import DatabaseManager
from services.task_service import TaskService
from services.notification_service import NotificationService

TASK_TITLE = range(1)


class TodoBot:
    """Класс бота для управления задачами."""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.task_service = TaskService(self.db)
        self.notification_service = NotificationService(self.db)
        self.application = None
    
    def setup_handlers(self):
        """Настраивает обработчики команд."""
        
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('add', self.add_task_start),
                CallbackQueryHandler(self.add_task_callback, pattern='add')
            ],
            states={
                TASK_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_task_title)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(conv_handler)
        self.application.add_handler(CommandHandler('list', self.list_tasks))
        self.application.add_handler(CommandHandler('complete', self.complete_task))
        self.application.add_handler(CommandHandler('delete', self.delete_task))
        self.application.add_handler(CommandHandler('stats', self.show_stats))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик /start."""
        user = update.effective_user
        
        self.db.connect()
        self.db.create_user(user.id, user.username, user.first_name, user.last_name)
        
        welcome_text = (
            f"👋 *Привет, {user.first_name}!*\n\n"
            "Я помогу тебе организовать свои задачи!\n\n"
            "*Что я умею:*\n"
            "➕ `/add` - Добавить задачу\n"
            "📋 `/list` - Список задач\n"
            "✅ `/complete <номер>` - Выполнить задачу\n"
            "🗑 `/delete <номер>` - Удалить задачу\n"
            "📊 `/stats` - Статистика"
        )
        
        keyboard = [
            [InlineKeyboardButton("➕ Добавить задачу", callback_data="add")],
            [InlineKeyboardButton("📋 Мои задачи", callback_data="list")],
            [InlineKeyboardButton("📊 Статистика", callback_data="stats")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def add_task_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Начинает добавление задачи."""
        await update.message.reply_text(
            "✏️ Введите *название задачи*:",
            parse_mode='Markdown'
        )
        return TASK_TITLE
    
    async def add_task_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Callback для кнопки добавления."""
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            "✏️ Введите *название задачи*:",
            parse_mode='Markdown'
        )
        return TASK_TITLE
    
    async def add_task_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет название задачи."""
        title = update.message.text
        user_id = update.effective_user.id
        
        success, message = await self.task_service.add_task(user_id, title)
        
        await update.message.reply_text(message, parse_mode='Markdown')
        return ConversationHandler.END
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Отменяет добавление."""
        await update.message.reply_text("❌ Добавление отменено")
        return ConversationHandler.END
    
    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает список задач."""
        user_id = update.effective_user.id
        result = await self.task_service.list_tasks(user_id)
        await update.message.reply_text(result, parse_mode='Markdown')
    
    async def complete_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмечает задачу выполненной."""
        user_id = update.effective_user.id
        
        if context.args:
            index = context.args[0]
            success, message = await self.task_service.complete_task(user_id, index)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            tasks = self.db.get_user_tasks(user_id)
            pending_tasks = [t for t in tasks if not t.is_completed()]
            
            if not pending_tasks:
                await update.message.reply_text("🎉 У вас нет активных задач!")
                return
            
            result = "✅ *Выберите задачу:*\n\n"
            for i, task in enumerate(pending_tasks, 1):
                result += f"{i}. {task.title}\n"
            result += "\nОтправьте: `/complete 1`"
            
            await update.message.reply_text(result, parse_mode='Markdown')
    
    async def delete_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Удаляет задачу."""
        user_id = update.effective_user.id
        
        if context.args:
            index = context.args[0]
            success, message = await self.task_service.delete_task(user_id, index)
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            tasks = self.db.get_user_tasks(user_id)
            
            if not tasks:
                await update.message.reply_text("📭 Нет задач для удаления")
                return
            
            result = "🗑 *Выберите задачу:*\n\n"
            for i, task in enumerate(tasks, 1):
                emoji = "✅" if task.is_completed() else "⭕️"
                result += f"{i}. {emoji} {task.title}\n"
            result += "\nОтправьте: `/delete 1`"
            
            await update.message.reply_text(result, parse_mode='Markdown')
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает статистику."""
        user_id = update.effective_user.id
        result = self.notification_service.get_daily_stats(user_id)
        await update.message.reply_text(result, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик кнопок."""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'list':
            result = await self.task_service.list_tasks(query.from_user.id)
            await query.edit_message_text(result, parse_mode='Markdown')
        elif query.data == 'stats':
            result = self.notification_service.get_daily_stats(query.from_user.id)
            await query.edit_message_text(result, parse_mode='Markdown')
    
    def run(self):
        """Запускает бота."""
        if not Config.validate():
            return
        
        self.db.connect()
        
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        self.setup_handlers()
        
        print("🤖 Todo List Bot запущен...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)