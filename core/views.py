from django.shortcuts import render
from account.models import TelegramProfile
from django.contrib.auth.decorators import login_required


def frontpage(request):
    return render(request, 'core/frontpage.html')

@login_required
def profile(request):
    try:
        tg_profile = TelegramProfile.objects.get(user=request.user)
        telegram_username = tg_profile.telegram_username
    except TelegramProfile.DoesNotExist:
        telegram_username = ""

    context = {
        'user': request.user,
        'telegram_username': telegram_username,
    }
    return render(request, 'core/profile.html', context)