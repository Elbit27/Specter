from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GoalViewSet, StepViewSet

router = DefaultRouter()
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'steps', StepViewSet, basename='step')


urlpatterns = [
    path('', views.goal_list, name='goal_page'),
    path('create/', views.goal_create_page, name='goal_create'),
    path('<int:pk>/edit/', views.goal_update_page, name='goal_update'),
    path('api/', include(router.urls)),
]