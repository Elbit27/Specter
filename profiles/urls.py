from django.urls import path
from . import views

urlpatterns = [
    path('change-username/', views.change_username, name='change-username'),
    path('change-email/', views.change_email, name='change-email'),
    path('verify-email-change/', views.verify_email_change, name='verify-email-change'),
    path('change-avatar/', views.change_avatar, name='change-avatar'),
]
