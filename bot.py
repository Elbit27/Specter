import os
import django
import telebot
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from schedule.models import Poma, Item, TelegramProfile
from django.contrib.auth.models import User


bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    tg_username_from_chat = message.from_user.username

    if not tg_username_from_chat:
        bot.reply_to(message, "У вас в настройках Telegram не задан публичный Username (имя пользователя). "
                              "Пожалуйста, установите его в настройках Telegram, чтобы бот мог вас узнать.")
        return

    profile = TelegramProfile.objects.filter(telegram_username__iexact=tg_username_from_chat).first()

    if profile:
        profile.telegram_chat_id = message.chat.id
        profile.save()

        bot.reply_to(message,
                     f"Привет, {profile.user.username}! Ваш аккаунт успешно распознан по нику @{tg_username_from_chat} и привязан к боту!")
    else:
        # Если такого ника на сайте нет
        bot.reply_to(message,
                     f"Привет! Я вижу ваш ник @{tg_username_from_chat}, но он не зарегистрирован ни на одном аккаунте нашего сайта. "
                     f"Пожалуйста, обратитесь к администратору или укажите этот ник в своем профиле на сайте.")



def save_user_link(message):
    username_input = message.text.strip()
    chat_id = message.chat.id

    user = User.objects.filter(username=username_input).first()

    if user:
        TelegramProfile.objects.update_or_create(
            user=user,
            defaults={'telegram_chat_id': chat_id}
        )
        bot.send_message(chat_id, f"Успешно! Аккаунт '{user.username}' привязан к этому чату.")
    else:
        msg = bot.send_message(chat_id, f"Пользователь с логином '{username_input}' не найден. Попробуйте еще раз /start")

@bot.message_handler(func=lambda message: True)
def add_poma(message):
    project_name = message.text.strip()
    chat_id = message.chat.id
    tg_profile = TelegramProfile.objects.filter(telegram_chat_id=chat_id).first()

    if not tg_profile:
        bot.reply_to(message, "Вы еще не привязали свой аккаунт. Введите команду /start")
        return
    user = tg_profile.user

    item = Item.objects.filter(name__iexact=project_name, user=user).first()

    if item:
        # Создаем запись Poma
        import datetime
        day_name = datetime.datetime.now().strftime('%A')  # Получаем текущий день (Monday, etc.)

        Poma.objects.create(
            item=item,
            day=day_name
        )
        bot.reply_to(message, f"✅ Помидорка добавлена в проект '{item.name}'!")
    else:
        bot.reply_to(message, f"❌ Проект '{project_name}' не найден. Сначала создай его на сайте.")


if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)