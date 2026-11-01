from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from account.views import verify_code_view, resend_code_view


account_patterns = [
    path('verify-code/', verify_code_view, name='account_verify_code'),
    path('resend-code/', resend_code_view, name='account_resend_code'),
    path('', include('allauth.urls')),
]

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include(account_patterns)),
    path('schedule/', include('schedule.urls')),
    path('report/', include('report.urls')),
    path('goal/', include('goal.urls')),
    path('todo/', include('todo.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)