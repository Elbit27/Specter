from django.contrib.auth.models import User
from schedule.models import TelegramProfile


def register_start_handlers(bot):

    @bot.message_handler(commands=['start'])
    def start(message):
        tg_username_from_chat = message.from_user.username

        if not tg_username_from_chat:
            bot.reply_to(
                message,
                "У вас не установлен Username в Telegram.\n"
                "Пожалуйста, установите Username в настройках Telegram, "
                "чтобы бот мог вас идентифицировать."
            )
            return

        profile = TelegramProfile.objects.filter(
            telegram_username__iexact=tg_username_from_chat
        ).first()

        if profile:
            profile.telegram_chat_id = message.chat.id
            profile.save()

            bot.reply_to(
                message,
                f"Привет, {profile.user.username}!\n"
                f"Твой Telegram @{tg_username_from_chat} успешно "
                f"привязан к твоему аккаунту."
            )
        else:
            bot.reply_to(
                message,
                f"Пользователь @{tg_username_from_chat} не найден.\n"
                f"Пожалуйста, сначала зарегистрируйтесь в приложении, "
                f"затем укажите свой Telegram Username в профиле."
            )


def save_user_link(message, bot):
    username_input = message.text.strip()
    chat_id = message.chat.id

    user = User.objects.filter(username=username_input).first()

    if user:
        TelegramProfile.objects.update_or_create(
            user=user,
            defaults={
                'telegram_chat_id': chat_id
            }
        )

        bot.send_message(
            chat_id,
            f"Готово! Пользователь '{user.username}' успешно "
            f"привязан к Telegram."
        )
    else:
        bot.send_message(
            chat_id,
            f"Пользователь '{username_input}' не найден.\n"
            f"Попробуйте ещё раз или используйте /start."
        )
