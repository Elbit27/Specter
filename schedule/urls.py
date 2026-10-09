from django.urls import path
from . import views
urlpatterns = [
    path('', views.schedule_view, name='schedule'),
    path('add_item/', views.ItemCreateView.as_view(), name='add-item'),
    path('update_poma/', views.update_poma, name='update_poma'),
    path('items/', views.ItemListView.as_view(), name='item-listing'),
]