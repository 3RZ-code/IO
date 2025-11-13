from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('readings/', views.DeviceReadingListCreate.as_view(), name='readings-list-create'),
    path('readings/<int:pk>/', views.DeviceReadingDetail.as_view(), name='readings-detail'),
    path('readings/filter/', views.DeviceReadingFilter.as_view(), name='readings-filter'),
]
