from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
import random
import string
import os

class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        # Код действует 10 минут
        return self.created_at >= timezone.now() - timedelta(minutes=10)

    @classmethod
    def generate_code(cls, user, email=None):
        code = ''.join(random.choices(string.digits, k=6))

        defaults = {'code': code, 'created_at': timezone.now()}

        if email is not None:
            defaults['email'] = email

        cls.objects.update_or_create(user=user, defaults=defaults)

        return code



class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    telegram_chat_id = models.BigIntegerField(unique=True, blank=True, null=True)

    class Meta:
        app_label = 'account'
        db_table = 'users_telegramprofile'
        verbose_name = 'Telegram profile'
        verbose_name_plural = 'Telegram profiles'

    def __str__(self):
        return f"Профиль {self.user.username} (TG-ник: {self.telegram_username})"



class Avatar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='avatar_owner')
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        blank=True
    )

    class Meta:
        app_label = 'account'
        db_table = 'users_avatar'
        verbose_name = "User's avatar"
        verbose_name_plural = "User's avatars"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_avatar = Avatar.objects.get(pk=self.pk).avatar
                if old_avatar and old_avatar != self.avatar:
                    if os.path.isfile(old_avatar.path):
                        os.remove(old_avatar.path)
            except Avatar.DoesNotExist:
                pass

        super(Avatar, self).save(*args, **kwargs)
