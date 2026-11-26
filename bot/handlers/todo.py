from asgiref.sync import sync_to_async

from todo.models import Todo
from django.utils import timezone
from datetime import timedelta

def register_todo_handlers(bot):

    @bot.message_handler(commands=['todo', 'todo_t'])
    async def todo_list(message, telegram_profile):
        user = telegram_profile.user
        yesterday = timezone.localdate() - timedelta(days=1)
        today = timezone.localdate()

        if message.text.startswith('/todo_t'):
            todos_qs = Todo.objects.filter(user=user, created_at__date=today)
            text = "📋 Ваши Todo на завтра:\n\n"
        else:
            todos_qs = Todo.objects.filter(user=user, created_at__date=yesterday)
            text = "📋 Ваши Todo на сегодня:\n\n"

        todos = await sync_to_async(list)(todos_qs)


        if not todos:
            await bot.reply_to(message, "У вас пока нет Todo.")
            return


        for todo in todos:
            status = "✅" if todo.completed else "⬜"
            text += f"{status} ({todo.id}) {todo.title}\n"

        await bot.reply_to(message, text)

    @bot.message_handler(commands=['todo_add'])
    async def todo_add(message, telegram_profile):
        user = telegram_profile.user
        lines = message.text.splitlines()

        if not lines:
            await bot.reply_to(message, "❌ Напишите хотя бы одну задачу.")
            return

        lines[0] = lines[0].replace('/todo_add', '', 1).strip()

        count = 0

        for line in lines:
            todo_title = line.strip()
            if todo_title:
                await Todo.objects.acreate(
                    user=user,
                    title=todo_title,
                )
                count += 1

        if count > 0:
            await bot.reply_to(
                message,
                f"✅ Успешно добавлено задач: {count} шт."
            )
        else:
            await bot.reply_to(
                message,
                "❌ Не удалось распознать задачи."
            )

    @bot.message_handler(commands=['done', 'delete'])
    async def todo_update(message):
        yesterday = timezone.localdate() - timedelta(days=1)

        if message.text.startswith('/done'):
            todo_id = message.text.replace('/done', '', 1).strip()
        else:
            todo_id = message.text.replace('/delete', '', 1).strip()

        todo = await Todo.objects.filter(created_at__date=yesterday, id=int(todo_id)).afirst()

        if not todo:
            await bot.reply_to(message, "❌ Todo не найдено.")
            return

        if message.text.startswith('/done'):
            todo.completed = True
            await todo.asave(update_fields=['completed'])
            message_text = f"✅ Задание '{todo.title}' выполнено! "
        else:
            await todo.adelete()
            message_text = f"🗑 Задание '{todo.title}' удалено!"

        await bot.reply_to(
            message,
            message_text
        )



