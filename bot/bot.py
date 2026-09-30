import os, django, telebot
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from bot.middleware import TelegramProfileMiddleware
from bot.handlers.start import register_start_handlers
from bot.handlers.poma import register_poma_handlers

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, use_class_middlewares=True)
bot.setup_middleware(TelegramProfileMiddleware(bot))

register_start_handlers(bot)
register_poma_handlers(bot)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)