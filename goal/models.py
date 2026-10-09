from django.db import models
from django.contrib.auth.models import User

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')


    GOAL_TYPE_CHOICES = [
        ('steps', 'Конкретные шаги'),
        ('numeric', 'Числовой счетчик'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    card_color = models.CharField(max_length=20, default='pink')
    prize = models.CharField(max_length=100, null=False)

    goal_type = models.CharField(max_length=10, choices=GOAL_TYPE_CHOICES, default='steps')
    current_value = models.IntegerField(default=0)
    target_value = models.IntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def uncompleted_steps(self):
        return [step for step in self.steps.all() if not step.completed]

    @property
    def completed_steps(self):
        return [step for step in self.steps.all() if step.completed]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Goals'
        ordering = ('created_at',)


class Step(models.Model):

    goal = models.ForeignKey('Goal', on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.goal.title})"

    class Meta:
        verbose_name_plural = 'Steps'
        ordering = ('created_at',)
