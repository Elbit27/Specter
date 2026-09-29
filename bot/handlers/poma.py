from datetime import datetime
from schedule.models import Poma, Item, TelegramProfile

def register_poma_handlers(bot):
    @bot.message_handler(func=lambda message: True)
    def add_poma(message):
        project_name = message.text.strip()
        chat_id = message.chat.id
        tg_profile = TelegramProfile.objects.filter(telegram_chat_id=chat_id).first()

        if not tg_profile:
            bot.reply_to(
                message,
                "Ваш Telegram ещё не привязан к аккаунту.\n"
                "Сначала выполните команду /start."
            )
            return

        user = tg_profile.user

        item = Item.objects.filter(name__iexact=project_name, user=user).first()

        if item:
            day_name = datetime.now().strftime('%A')
            Poma.objects.create(item=item, day=day_name)

            bot.reply_to(
                message,
                f"✅ Poma добавлена в расписание "
                f"'{item.name}'!"
            )
        else:
            bot.reply_to(
                message,
                f"❌ Проект '{project_name}' не найден.\n"
                f"Сначала добавьте этот проект в расписание."
            )
