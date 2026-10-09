from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo
from . import serializers
from django.views import generic
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
import json


@login_required
def todo_list(request):
    yesterday = timezone.localdate() - timedelta(days=1)

    todo = Todo.objects.filter(
        user=request.user,
        created_at__date = yesterday
    ).order_by('completed', 'created_at')
    return render(request, 'todo/todo_list.html', {'todo': todo})

class TodoCreateView(generic.View):
    template_name = 'todo/add_todo.html'

    def get(self, request, *args, **kwargs):
        todos = Todo.objects.filter(user=request.user)
        return render(request, self.template_name, {'todos': todos})

    def post(self, request, *args, **kwargs):
        data = {
            'title': request.POST.get('title', '').strip(),
            'description': request.POST.get('description', '').strip(),
        }

        serializer = serializers.TodoCreateSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return redirect('todo')
        else:
            return render(request, self.template_name, {
                'todos': Todo.objects.filter(user=request.user),
                'form_errors': serializer.errors
            })

class TodoUpdateView(generic.UpdateView):
    def patch(self, request, *args, **kwargs):
        todo = get_object_or_404(
            Todo,
            pk=kwargs['pk'],
            user=request.user
        )

        data = json.loads(request.body)

        todo.completed = data.get('completed', todo.completed)
        todo.save(update_fields=['completed'])

        return JsonResponse({
            'success': True,
            'completed': todo.completed
        })