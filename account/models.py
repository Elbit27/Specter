from django.db import models
from django.utils import timezone
import random
import string
from datetime import timedelta
from django.contrib.auth.models import User

class EmailVerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        # Код действует 10 минут
        return self.created_at >= timezone.now() - timedelta(minutes=10)

    @classmethod
    def generate_code(cls, user):
        code = ''.join(random.choices(string.digits, k=6))
        cls.objects.update_or_create(user=user, defaults={'code': code, 'created_at': timezone.now()})
        return code

