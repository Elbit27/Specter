from datetime import timedelta
from django.utils import timezone
from asgiref.sync import sync_to_async
from todo.models import Todo

async def get_todos_tool(user_id: int, day: str = 'today'):
    """
    Возвращает список задач пользователя.
    Аргумент day принимает значения: 'today' (задачи на сегодня) или 'tomorrow' (задачи на завтра).
    """
    yesterday = timezone.localdate() - timedelta(days=1)
    today = timezone.localdate()

    target_date = today if day == "tomorrow" else yesterday
    todos_qs = Todo.objects.filter(user_id=user_id, created_at__date=target_date)
    todos = await sync_to_async(list)(todos_qs)

    if not todos:
        return f"Задач на {day} пока нет."

    result = []
    for todo in todos:
        status = "Выполнено" if todo.completed else "Не выполнено"
        result.append(f"ID {todo.id}: {todo.title} [{status}]")

    return "\n".join(result)


async def add_todo_tool(user_id: int, titles: list[str]) -> str:
    """
    Добавляет одну или несколько новых задач в список дел пользователя.
    titles — список строк с названиями задач.
    """
    created = []
    for title in titles:
        clean_title = title.strip()
        if clean_title:
            todo = await Todo.objects.acreate(user_id=user_id, title=clean_title)
            created.append(f"'{todo.title}' (ID {todo.id})")

    if not created:
        return "Не удалось добавить задачи: список пуст."

    return f"Успешно добавлены задачи: {', '.join(created)}"


async def update_todo_tool(user_id: int, todo_id: int, action: str) -> str:
    """
    Отмечает задачу выполненной или удаляет её по ID.
    action принимает значения: 'complete' (выполнить) или 'delete' (удалить).
    """
    # Ищем задачу с учетом user_id для безопасности, используем асинхронный afirst()!
    todo = await Todo.objects.filter(user_id=user_id, id=todo_id).afirst()

    if not todo:
        return f"Задача с ID {todo_id} не найдена."

    if action == "complete":
        todo.completed = True
        await todo.asave(update_fields=['completed'])
        return f"Задача '{todo.title}' (ID {todo_id}) отмечена как выполненная."
    elif action == "delete":
        title = todo.title
        await todo.adelete()
        return f"Задача '{title}' (ID {todo_id}) удалена."

    return "Неизвестное действие."


