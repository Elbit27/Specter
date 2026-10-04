from rest_framework import serializers
from .models import Todo

class TodoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['title', 'description',]

