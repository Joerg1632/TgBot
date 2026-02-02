"""
run.py

Главный файл для старта Telegram-бота.
Регистрирует все обработчики и запускает поллинг.
"""
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import TG_BOT_API_TOKEN
from handlers.handlers import register_message_handlers
from callbacks.callbacks import register_callback_handlers
from services.cashback_history import load_paid_cashbacks

# Инициализация бота и диспетчера
bot = Bot(token=TG_BOT_API_TOKEN)
dp = Dispatcher(bot)

# Настройка логгера
logging.basicConfig(level=logging.INFO)

def register_all_handlers():
    """Инициализация файла с историей выплат при запуске"""
    load_paid_cashbacks()  # Создаст файл если его нет
    register_message_handlers(dp, bot)
    register_callback_handlers(dp, bot)
if __name__ == '__main__':
    register_all_handlers()
    logging.info("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
