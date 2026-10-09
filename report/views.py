from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count
from datetime import timedelta, date
from django.utils import timezone
from schedule.models import Poma  # если у тебя модель так называется
from django.shortcuts import render
from django.db.models.functions import ExtractWeekDay
import calendar



def report_page(request):
    return render(request, 'core/report.html')


from django.db.models.functions import TruncDate

@api_view(['GET'])
def report_data(request):
    period = request.GET.get('period', 'week')
    offset = int(request.GET.get('offset', 0))
    today = timezone.now().date()

    if period == 'week':
        start_date = today - timedelta(days=today.weekday()) + timedelta(weeks=offset)
        end_date = start_date + timedelta(days=6)
    elif period == 'month':
        # Вычисляем первый день месяца без циклов
        total_months = today.year * 12 + (today.month - 1) + offset
        year, month = divmod(total_months, 12)
        start_date = date(year, month + 1, 1)
        last_day = calendar.monthrange(year, month + 1)[1]
        end_date = date(year, month + 1, last_day)
    elif period == 'year':
        year = today.year + offset
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
    else:
        return Response({"error": "Invalid period"}, status=400)

    # Группируем по конкретным датам, а не по дням недели
    queryset = (
        Poma.objects
        .filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Для недели вернем старый формат (Mon, Tue...), для остального — даты
    if period == 'week':
        days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
        data_dict = {day: 0 for day in days_map.values()}
        for item in queryset:
            weekday_name = days_map[item['date'].weekday()]
            data_dict[weekday_name] += item['count']
        result = [{'day': k, 'count': v} for k, v in data_dict.items()]
    else:
        # Возвращаем [{'date': '2026-05-01', 'count': 5}, ...]
        result = list(queryset)

    return Response(result)


@api_view(['GET'])
def report_detail(request):
    # Добавляем select_related, чтобы избежать проблемы N+1 запросов
    pomas = Poma.objects.select_related('item').all().order_by('-created_at')

    result = []
    for p in pomas:
        result.append({
            "id": p.id,
            "date_display": p.created_at.strftime('%d %b %Y'),
            "time_display": p.created_at.strftime('%H:%M'),
            "item_name": p.item.name,  # Теперь это сработает быстро
            "task_label": "Specter",
            "duration": 60
        })
    return Response(result)