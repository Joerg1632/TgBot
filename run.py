import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import API_TOKEN
from handlers import register_message_handlers
from callbacks import register_callback_handlers

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

def register_all_handlers():
    register_message_handlers(dp)
    register_callback_handlers(dp, bot)

if __name__ == '__main__':
    register_all_handlers()
    logging.info("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
