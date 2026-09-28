from rest_framework import serializers
from .models import Todo

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['title', 'description',]

