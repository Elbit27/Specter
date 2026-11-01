from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tg-profile', views.TelegramProfileViewSet, basename='tg-profile')

urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('profile/', views.profile, name='profile'),
    path('api/', include(router.urls)),
]