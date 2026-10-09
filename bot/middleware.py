from telebot.handler_backends import BaseMiddleware
from schedule.models import TelegramProfile


class TelegramProfileMiddleware(BaseMiddleware):
    def __init__(self, bot):
        super().__init__()

        self.bot = bot
        self.update_types = ['message']

    def pre_process(self, message, data):
        if message.text == '/start':
            return

        profile = TelegramProfile.objects.filter(telegram_chat_id=message.chat.id).first()

        if not profile:
            self.bot.reply_to(
                message,
                "Ваш Telegram не привязан к аккаунту.\n"
                "Сначала выполните команду /start."
            )
            return

        data['telegram_profile'] = profile

    def post_process(self, message, data, exception):
        pass