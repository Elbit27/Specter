from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Todo
from django.views import generic
from . import serializers
from django.utils import timezone
from datetime import timedelta



@login_required
def todo_list(request):
    yesterday = timezone.localdate() - timedelta(days=1)

    todo = Todo.objects.filter(
        user=request.user,
        created_at__date = yesterday
    )
    return render(request, 'todo/todo_list.html', {'todo': todo})

class TaskCreateView(generic.View):
    template_name = 'todo/add_task.html'

    def get(self, request, *args, **kwargs):
        tasks = Todo.objects.filter(user=request.user)
        return render(request, self.template_name, {'tasks': tasks})

    def post(self, request, *args, **kwargs):
        data = {
            'title': request.POST.get('title', '').strip(),
            'description': request.POST.get('description', '').strip(),
        }

        serializer = serializers.TaskCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return redirect('todo')
        else:
            return render(request, self.template_name, {
                'tasks': Todo.objects.filter(user=request.user),
                'form_errors': serializer.errors
            })


# @login_required
# def goal_create_page(request, pk=None):
#     goal = None
#     return render(request, 'goal/CreateUpdateGoal.html', {'goal': goal})
#
# @login_required
# def goal_update_page(request, pk=None):
#     goal = get_object_or_404(Goal.objects.prefetch_related('steps'), pk=pk)
#     return render(request, 'goal/CreateUpdateGoal.html', {'goal': goal})
