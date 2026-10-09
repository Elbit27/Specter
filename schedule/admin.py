from django.contrib import admin
from .models import Item, Poma, TelegramProfile

class PomaInline(admin.TabularInline):  # можно StackedInline для вертикального вида
    model = Poma
    extra = 1  # сколько пустых форм показывать для добавления
    fields = ('day',)  # поля, которые будут видны

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'poma_count')  # покажет количество Poma в списке
    inlines = [PomaInline]  # блок с Poma внутри Item

@admin.register(Poma)
class PomaAdmin(admin.ModelAdmin):
    list_display = ('day', 'item')  # стандартная админка для Poma

@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'telegram_chat_id')
