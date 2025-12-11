from django.urls import path
from .views import OptimizationRecommendation

urlpatterns = [
    path('', OptimizationRecommendation.as_view(), name='optimization-index'),
]