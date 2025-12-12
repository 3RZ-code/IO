from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router dla ViewSet
router = DefaultRouter()
router.register(r'schedules', views.ScheduleViewSet, basename='schedule')

urlpatterns = [
    # Główny endpoint modułu
    path('', views.index, name='index'),
    
    # ViewSet routes (pełny CRUD + akcje dodatkowe)
    path('', include(router.urls)),
    
    # # Filtrowanie harmonogramów
    # path('schedules-filter/', views.ScheduleFilter.as_view(), name='schedule-filter'),
]