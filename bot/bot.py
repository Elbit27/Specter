import os, django, threading, asyncio, traceback
from telebot.async_telebot import AsyncTeleBot
from django.conf import settings




os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.middleware import TelegramProfileMiddleware
from bot.handlers.start import register_start_handlers
from bot.handlers.poma import register_poma_handlers
from bot.handlers.todo import register_todo_handlers
from bot.handlers.ai import register_ai_handlers


bot = AsyncTeleBot(settings.TELEGRAM_BOT_TOKEN)
bot.setup_middleware(TelegramProfileMiddleware(bot))

register_start_handlers(bot)
register_poma_handlers(bot)
register_todo_handlers(bot)
register_ai_handlers(bot)

async def start_bot_polling():
    print('Асинхронный бот успешно запущен...')
    try:
        await bot.infinity_polling()
    except Exception as e:
        print("Ошибка в работе бота:")
        traceback.print_exc()

def run_async_loop():
    asyncio.run(start_bot_polling())


# Запускаем бота в фоновом потоке, чтобы он не блокировал Gunicorn и деплой Render
bot_thread = threading.Thread(target=run_async_loop, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    print("Бот запущен вручную через __main__...")
    bot_thread.join()

# run bot in terminal code: python3 -m bot.bot