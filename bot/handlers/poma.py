from datetime import datetime

from schedule.models import Poma, Item


def register_poma_handlers(bot):

    @bot.message_handler(commands=['poma'])
    async def add_poma(message, telegram_profile):
        parts = message.text.split(maxsplit=2)

        if len(parts) < 2:
            await bot.reply_to(
                message,
                "❌ Укажите название проекта.\n"
                "Например: `/poma Project` или `/poma Project 3`"
            )
            return

        project_name = parts[1].strip()
        count = 1

        if len(parts) == 3:
            try:
                count = int(parts[2].strip())
                if count <= 0:
                    raise ValueError
            except ValueError:
                await bot.reply_to(message, "❌ Количество должно быть целым числом больше нуля.")
                return


        user = telegram_profile.user

        item = await Item.objects.filter(
            name__iexact=project_name,
            user=user
        ).afirst()

        if item:
            day_name = datetime.now().strftime('%A')

            for _ in range(count):
                await Poma.objects.acreate(
                    item=item,
                    day=day_name
                )

            await bot.reply_to(
                message,
                f"✅ Poma {item.name} добавлена в расписание: {count} шт.!"
            )
        else:
            await bot.reply_to(
                message,
                f"❌ Проект '{project_name}' не найден.\n"
                f"Сначала добавьте этот проект в расписание."
            )
