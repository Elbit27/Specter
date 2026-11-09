from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
import random
import string

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

