from django.utils import timezone

from schedule.models import Poma, Item

async def add_poma_tool(user_id: int, project_name: str, count: int):
    """
    Добавляет pom'ы - помидорки отчёт. Одна помидорка 1 час продуктивного времяпровождения.

    Args:
        user_id: ID пользователя в базе данных.
        project_name: Название проекта, над которым работал пользователь.
        count: Количество помидорок (часов) для добавления (по умолчанию 1).
    """

    if count <= 0:
        return "❌ Количество помидорок должно быть больше нуля."

    item = await Item.objects.filter(
        name__iexact=project_name.strip(),
        user=user_id
    ).afirst()


    if not item:
        return (
            f"❌ Проект '{project_name}' не найден.\n"
            f"Сначала добавьте этот проект в расписание."
        )

    day_name = timezone.localtime().strftime('%A')

    pomas = [Poma(item=item, day=day_name) for _ in range(count)]
    await Poma.objects.abulk_create(pomas)

    return f"✅ Poma для проекта «{item.name}» добавлена в расписание: {count} шт. ({day_name})!"



