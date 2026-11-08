import random
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login
from allauth.account.models import EmailAddress
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from account.forms import OnboardingForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings

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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def change_username(request):
    user = request.user

    new_username = request.data.get('username', '').strip()
    
    if not new_username:
        return Response(
            {'error': 'Username is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.username == new_username:
        return Response(
            {'message': 'Username has not changed'},
            status=status.HTTP_200_OK
        )

    if User.objects.filter(username=new_username).exists():
        return Response(
            {'error': 'This username is already taken'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.username = new_username
    user.save(update_fields=['username'])

    return Response(
        {'message': 'Username successfully changed',
         'username': user.username},
        status=status.HTTP_200_OK
    )




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_email(request):
    new_email = request.data.get('email', '').strip().lower()

    if not new_email:
        return Response(
            {'error': 'Введите новый email.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email__iexact=new_email).exclude(
        pk=request.user.pk
    ).exists():
        return Response(
            {'error': 'Этот email уже используется.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if request.user.email.lower() == new_email:
        return Response(
            {'error': 'Это уже ваш текущий email.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    code = EmailVerificationCode.generate_code(
        user=request.user,
        email=new_email
    )

    context = {
        'verification_code': code,
        'user': request.user,
    }

    message = render_to_string(
        'account/email/change_email_confirmation_message'
        '.txt',
        context
    )


    send_mail(
        subject='Specter — подтверждение нового email',
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[new_email],
        fail_silently=False,
    )

    return Response(
        {'message': 'Код подтверждения отправлен на новый email.'},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_email_change(request):
    code = request.data.get('code', '').strip()

    if not code:
        return Response({'error': 'Введите код подтверждения.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        verification = EmailVerificationCode.objects.get(user=request.user)
    except EmailVerificationCode.DoesNotExist:
        return Response(
            {'error': 'Код подтверждения не найден.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not verification.is_valid():
        verification.delete()
        return Response(
            {'error': 'Срок действия кода истёк. Запросите новый код.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if verification.code != code:
        return Response(
            {'error': 'Неверный код подтверждения.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    new_email = verification.email

    if not new_email:
        return Response(
            {'error': 'Адрес электронной почты не найден.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email__iexact=new_email).exclude(
        pk=request.user.pk
    ).exists():
        verification.delete()
        return Response(
            {'error': 'Этот email уже используется другим пользователем.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    EmailAddress.objects.filter(
        user=request.user,
        primary=True
    ).update(primary=False)

    email_address, created = EmailAddress.objects.get_or_create(
        user=request.user,
        email=new_email,
        defaults={
            'verified': True,
            'primary': True
        }
    )

    if not created:
        email_address.verified = True
        email_address.primary = True
        email_address.save(update_fields=['verified', 'primary'])

    request.user.email = new_email
    request.user.save(update_fields=['email'])

    verification.delete()

    return Response(
        {
            'message': 'Email успешно изменён!',
            'email': new_email
        },
        status=status.HTTP_200_OK
    )