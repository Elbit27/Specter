from rest_framework import serializers
from profiles.models import TelegramProfile


class TelegramProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramProfile
        fields = '__all__'
        read_only_fields = ['user']
