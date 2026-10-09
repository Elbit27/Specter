from datetime import datetime

from schedule.models import Poma, Item


def register_poma_handlers(bot):

    @bot.message_handler(commands=['poma'])
    def add_poma(message, telegram_profile):
        project_name = message.text.replace('/poma', '', 1).strip()

        if not project_name:
            bot.reply_to(
                message,
                "Укажите название проекта.\n"
                "Например: /poma Project"
            )
            return

        user = telegram_profile.user

        item = Item.objects.filter(
            name__iexact=project_name,
            user=user
        ).first()

        if item:
            day_name = datetime.now().strftime('%A')

            Poma.objects.create(
                item=item,
                day=day_name
            )

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
