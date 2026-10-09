from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_page, name='report_page'),      # HTML страница
    path('data/', views.report_data, name='report_data'),  # API данные
    path('report_detail/', views.report_detail, name='report_detail'),
]
