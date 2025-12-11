from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'alerts', views.AlertViewSet, basename='alert')
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'preferences', views.NotificationPreferencesViewSet, basename='notification-preferences')

urlpatterns = [
    path('', include(router.urls)),
]