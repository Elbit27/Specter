from rest_framework import serializers
from account.models import TelegramProfile


class TelegramProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramProfile
        fields = '__all__'
        read_only_fields = ['user']
