from django.urls import path
from . import views
from data_acquisition.views import DeviceReadingList

urlpatterns = [
    path('', views.index, name='index'),
    path("api/readings/",DeviceReadingList.as_view(), name="device_readings"),
]