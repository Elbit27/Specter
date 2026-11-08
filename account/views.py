import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login
from allauth.account.models import EmailAddress


from account.forms import OnboardingForm

from .models import EmailVerificationCode


@login_required
def complete_profile(request):
    if request.method == 'POST':
        form = OnboardingForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = OnboardingForm(instance=request.user)
    return render(request, 'account/complete_profile.html', {'form': form})


def _generate_and_send_code(user):
    EmailVerificationCode.objects.filter(user=user).delete()

    new_code = f"{random.randint(100000, 999990)}"

    EmailVerificationCode.objects.create(
        user=user,
        code=new_code
    )

    send_mail(
        subject="Код подтверждения Unify",
        message=f"Ваш код подтверждения: {new_code}",
        from_email="noreply@unify.academy",
        recipient_list=[user.email],
        fail_silently=False,
    )


def verify_code_view(request):
    if request.method == 'POST':
        input_code = request.POST.get('code')
        try:
            verification = EmailVerificationCode.objects.get(code=input_code)

            if verification.is_valid():
                user = verification.user

                email_obj, created = EmailAddress.objects.get_or_create(
                    user=user,
                    email=user.email
                )
                email_obj.verified = True
                email_obj.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                verification.delete()

                messages.success(request, "Почта подтверждена, добро пожаловать!")
                return redirect('/')
            else:
                messages.error(request, "Код просрочен.")

        except EmailVerificationCode.DoesNotExist:
            messages.error(request, "Неверный код подтверждения.")

    return render(request, 'account/email_confirm.html')


from django.views.decorators.http import require_POST
from django.http import JsonResponse


@require_POST
def resend_code_view(request):
    try:
        user_id = request.session.get('account_user_id')

        if not user_id:
            last_code_entry = EmailVerificationCode.objects.order_by('-id').first()
            if last_code_entry:
                user = last_code_entry.user
            else:
                return JsonResponse({'status': 'error', 'message': 'Пользователь не найден в сессии.'}, status=400)
        else:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(pk=user_id)

        _generate_and_send_code(user)
        return JsonResponse({'status': 'success', 'message': 'Новый код отправлен на почту.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

