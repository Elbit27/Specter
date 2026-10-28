from rest_framework.response import Response
from rest_framework.decorators import action
from goal import serializers
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from goal.models import Goal, Step
from django.contrib.auth.decorators import login_required


@login_required
def goal_list(request):
    goals = Goal.objects.filter(user=request.user, is_archived=False).prefetch_related('steps')
    return render(request, 'goal/goal_list.html', {'goals': goals})

@login_required
def goal_create_page(request):
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

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user, is_archived=False).prefetch_related('steps')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        return serializers.GoalSerializer

    @action(detail=False, methods=['get'])
    def archived(self, request):
        archived_goals = Goal.objects.filter(user=request.user, is_archived=True).prefetch_related('steps')
        serializer = self.get_serializer(archived_goals, many=True)
        return Response(serializer.data)

