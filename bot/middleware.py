from telebot.handler_backends import BaseMiddleware
from profiles.models import TelegramProfile


class TelegramProfileMiddleware(BaseMiddleware):
    def __init__(self, bot):
        super().__init__()

        self.bot = bot
        self.update_types = ['message']

    async def pre_process(self, message, data):
        if message.text and message.text.startswith('/start'):
            return

        profile = await TelegramProfile.objects.select_related('user').filter(telegram_chat_id=message.chat.id).afirst()

        if not profile:
            await self.bot.reply_to(
                message,
                "Ваш Telegram не привязан к аккаунту.\n"
                "Сначала выполните команду /start."
            )
            return

        data['telegram_profile'] = profile

    async def post_process(self, message, data, exception):
        pass