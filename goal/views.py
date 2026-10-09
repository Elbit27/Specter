from goal import serializers
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from goal.models import Goal, Step
from django.contrib.auth.decorators import login_required


@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user).prefetch_related('steps')
    return render(request, 'goal/goal_list.html', {'goals': goals})

@login_required
def goal_create_page(request, pk=None):
    goal = None
    return render(request, 'goal/CreateUpdateGoal.html', {'goal': goal})

@login_required
def goal_update_page(request, pk=None):
    goal = get_object_or_404(Goal.objects.prefetch_related('steps'), pk=pk)
    return render(request, 'goal/CreateUpdateGoal.html', {'goal': goal})



class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = serializers.StepSerializer


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        return serializers.GoalSerializer

