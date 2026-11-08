from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail
from allauth.account.models import EmailAddress
from account.models import EmailVerificationCode, Avatar


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





@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def change_avatar(request):
    avatar_file = request.FILES.get('avatar')

    if not avatar_file:
        return Response(
            {'error': 'Изображение не было передано.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Проверяем, что файл является изображением
    serializer = serializers.ImageField()

    try:
        serializer.run_validation(avatar_file)
    except serializers.ValidationError:
        return Response(
            {'error': 'Загрузите корректное изображение.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    avatar, created = Avatar.objects.get_or_create(
        user=request.user
    )

    avatar.avatar = avatar_file
    avatar.save(update_fields=['avatar'])

    return Response(
        {
            'message': 'Аватар успешно обновлён.',
            'avatar_url': request.build_absolute_uri(avatar.avatar.url)
        },
        status=status.HTTP_200_OK
    )