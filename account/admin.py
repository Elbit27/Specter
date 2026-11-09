from django.contrib import admin
from profiles.models import TelegramProfile, Avatar

@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_username', 'telegram_chat_id')
    search_fields = ('user__username', 'telegram_username')

@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar',)
    search_fields = ('user', 'avatar')