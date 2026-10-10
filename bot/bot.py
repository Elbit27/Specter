import os, django, telebot
from django.conf import settings
import threading



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.middleware import TelegramProfileMiddleware
from bot.handlers.start import register_start_handlers
from bot.handlers.poma import register_poma_handlers
from bot.handlers.todo import register_todo_handlers

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, use_class_middlewares=True)
bot.setup_middleware(TelegramProfileMiddleware(bot))

register_start_handlers(bot)
register_poma_handlers(bot)
register_todo_handlers(bot)



def start_bot_polling():
    print("Бот успешно запущен в фоновом потоке...")
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка в работе бота: {e}")

# Запускаем бота в фоновом потоке, чтобы он не блокировал Gunicorn и деплой Render
bot_thread = threading.Thread(target=start_bot_polling, daemon=True)
bot_thread.start()

if __name__ == '__main__':
    print("Бот запущен вручную через __main__...")
    bot_thread.join()