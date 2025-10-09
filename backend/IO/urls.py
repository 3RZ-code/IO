"""
URL configuration for IO project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('data-acquisition/', include('data_acquisition.urls')),
    path('analysis-reporting/', include('analysis_reporting.urls')),
    path('forecasting/', include('forecasting.urls')),
    path('optimization-control/', include('optimization_control.urls')),
    path('alarm-alert/', include('alarm_alert.urls')),
    path('communication/', include('communication.urls')),
    path('security/', include('security.urls')),
    path('simulation/', include('simulation.urls')),
    path('', include("data_acquisition.urls")),
]
