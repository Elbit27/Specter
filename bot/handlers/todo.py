from todo.models import Todo
from django.utils import timezone
from datetime import timedelta




def register_todo_handlers(bot):

    @bot.message_handler(commands=['todo', 'todo_t'])
    def todo_list(message, telegram_profile):
        user = telegram_profile.user
        yesterday = timezone.localdate() - timedelta(days=1)
        today = timezone.localdate()

        if message.text.startswith('/todo_t'):
            todos = Todo.objects.filter(user=user, created_at__date=today)
            text = "📋 Ваши Todo на завтра:\n\n"
        else:
            todos = Todo.objects.filter(user=user, created_at__date=yesterday)
            text = "📋 Ваши Todo на сегодня:\n\n"

        if not todos.exists():
            bot.reply_to(
                message,
                "У вас пока нет Todo.")
            return


        for todo in todos:
            status = "✅" if todo.completed else "⬜"
            text += f"{status} ({todo.id}) {todo.title}\n"

        bot.reply_to(message, text)

    @bot.message_handler(commands=['todo_add'])
    def todo_add(message, telegram_profile):
        user = telegram_profile.user
        lines = message.text.splitlines()

        if not lines:
            bot.reply_to(message, "❌ Напишите хотя бы одну задачу.")
            return

        lines[0] = lines[0].replace('/todo_add', '', 1).strip()

        count = 0

        for line in lines:
            todo_title = line.strip()
            if todo_title:
                Todo.objects.create(
                    user=user,
                    title=todo_title,
                )
                count += 1

        if count > 0:
            bot.reply_to(
                message,
                f"✅ Успешно добавлено задач: {count} шт."
            )
        else:
            bot.reply_to(
                message,
                "❌ Не удалось распознать задачи."
            )

    @bot.message_handler(commands=['done', 'delete'])
    def todo_update(message):
        yesterday = timezone.localdate() - timedelta(days=1)

        if message.text.startswith('/done'):
            todo_id = message.text.replace('/done', '', 1).strip()
        else:
            todo_id = message.text.replace('/delete', '', 1).strip()

        todo = Todo.objects.filter(created_at__date=yesterday, id=int(todo_id)).first()

        if not todo:
            bot.reply_to(message, "❌ Todo не найдено.")
            return

        if message.text.startswith('/done'):
            todo.completed = True
            todo.save(update_fields=['completed'])
            message_text = f"✅ Задание '{todo.title}' выполнено! "
        else:
            todo.delete()
            message_text = f"🗑 Задание '{todo.title}' удалено!"

        bot.reply_to(
            message,
            message_text
        )



