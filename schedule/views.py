from rest_framework import generics
from django.shortcuts import render, redirect
from django.views import generic
from . import serializers
from .models import Item, Poma
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required


@login_required(login_url='/api/v1/accounts/login/')
def schedule_view(request):
    items = Item.objects.all()
    days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


    now = timezone.now()
    django_today_index = now.weekday()
    js_today_index = django_today_index

    days_since_monday = django_today_index
    start_of_week = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)

    item_day_counts = {}

    for item in items:
        item_day_counts[item.id] = {}
        for i, rus_day in enumerate(days):
            date_of_day_in_week = (start_of_week + timedelta(days=i)).date()

            if date_of_day_in_week <= now.date():
                count = Poma.objects.filter(
                    item=item,
                    created_at__date=date_of_day_in_week
                ).count()
                item_day_counts[item.id][rus_day] = count
            else:
                item_day_counts[item.id][rus_day] = ""

    return render(request, 'schedule/schedule.html', {
        'items': items,
        'days': days,
        'item_day_counts': item_day_counts,
        'today_index': js_today_index,
    })


class ItemCreateView(generic.View):
    template_name = 'schedule/add_item.html'

    def get(self, request, *args, **kwargs):
        items = Item.objects.filter(user=request.user)
        return render(request, self.template_name, {'items': items})

    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name', '').strip(),
        }

        serializer = serializers.ItemCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return redirect('schedule')  # имя URL, а не путь
        else:
            return render(request, self.template_name, {
                'items': Item.objects.filter(user=request.user),
                'form_errors': serializer.errors
            })


@csrf_exempt
def update_poma(request):
    print(request.POST)

    if request.method != "POST":
        return JsonResponse(
            {"status": "error", "message": "Invalid method"},
            status=405
        )

    try:
        item_id = request.POST.get("item_id")
        day_index = int(request.POST.get("day"))
        diff = int(request.POST.get("diff"))

        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        day = days[day_index]

        item = Item.objects.get(id=item_id)

        now = timezone.now()

        start_of_week = (
            now.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            - timedelta(days=now.weekday())
        )

        target_date = start_of_week + timedelta(days=day_index)

        if diff > 0:
            for _ in range(diff):
                Poma.objects.create(
                    item=item,
                    day=day,
                    created_at=target_date
                )

        elif diff < 0:
            day_start = target_date.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

            day_end = day_start + timedelta(days=1)

            for _ in range(abs(diff)):
                last = Poma.objects.filter(
                    item=item,
                    day=day,
                    created_at__gte=day_start,
                    created_at__lt=day_end
                ).last()

                if last:
                    last.delete()

        return JsonResponse({"status": "success"})

    except Exception as e:
        print("UPDATE POMA ERROR:", e)

        return JsonResponse(
            {
                "status": "error",
                "message": str(e)
            },
            status=400
        )

class ItemListView(generics.ListAPIView):
    queryset = Item.objects.all()
    serializer_class = serializers.ItemSerializer

