from django.db import models
from django.contrib.auth.models import User

class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    telegram_chat_id = models.BigIntegerField(unique=True, blank=True, null=True)

    class Meta:
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
        verbose_name = "User's avatar"
        verbose_name_plural = "User's avatars"

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_instance = Avatar.objects.get(pk=self.pk)
                old_avatar = old_instance.avatar

                if old_avatar and old_avatar != self.avatar and old_avatar.name != self._meta.get_field(
                        'avatar').default:
                    if old_avatar.storage.exists(old_avatar.name):
                        old_avatar.storage.delete(old_avatar.name)

            except Avatar.DoesNotExist:
                pass

        super(Avatar, self).save(*args, **kwargs)