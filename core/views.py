from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

from account.models import TelegramProfile, Avatar
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from . import serializers


def frontpage(request):
    return render(request, 'core/frontpage.html')

@login_required
def profile(request):
    try:
        tg_profile = TelegramProfile.objects.get(user=request.user)
        telegram_username = tg_profile.telegram_username
        avatar_object, created = Avatar.objects.get_or_create(user=request.user)
        avatar = avatar_object.avatar

    except TelegramProfile.DoesNotExist:
        telegram_username = ""
        avatar = ""

    context = {
        'user': request.user,
        'telegram_username': telegram_username,
        'avatar': avatar,
    }
    return render(request, 'core/profile.html', context)


class TelegramProfileViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.TelegramProfileSerializer

    def get_queryset(self):
        return TelegramProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        # Кастомный эндпоинт для работы с профилем текущего юзера без ID: /api/telegram/current/

    @action(detail=False, methods=['get', 'post', 'put', 'patch', 'delete'])
    def current(self, request):
        instance = TelegramProfile.objects.filter(user=request.user).first()

        # GET: Получить данные
        if request.method == 'GET':
            if not instance:
                return Response({"tg_profile": ""}, status=status.HTTP_200_OK)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        # POST или PUT/PATCH: Создать или Обновить
        elif request.method in ['POST', 'PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            if instance:
                serializer = self.get_serializer(instance, data=request.data, partial=partial)
            else:
                serializer = self.get_serializer(data=request.data)

            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user)
            return Response(serializer.data)

        # DELETE: Удалить привязку
        elif request.method == 'DELETE':
            if instance:
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "Не найдено"}, status=status.HTTP_444_NOT_FOUND)
        return None