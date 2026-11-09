from django.urls import path, include
from . import views as core_views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('tg-profile', core_views.TelegramProfileViewSet, basename='tg-profile')

urlpatterns = [
    path('', core_views.frontpage, name='frontpage'),
    path('profile/', core_views.profile, name='profile'),
    path('api/', include(router.urls)),
]