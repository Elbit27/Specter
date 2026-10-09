from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# from .views import GoalViewSet, StepViewSet

# router = DefaultRouter()
# router.register(r'goals', GoalViewSet, basename='goal')
# router.register(r'steps', StepViewSet, basename='step')


urlpatterns = [
    path('', views.todo_list, name='todo'),
    path('add_todo/', views.TodoCreateView.as_view(), name='add-todo'),
    path('<int:pk>/', views.TodoUpdateView.as_view(), name='update-todo'),
    # path('<int:pk>/edit/', views.goal_update_page, name='goal_update'),
    # path('api/', include(router.urls)),
]