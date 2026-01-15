from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'criteria', views.ReportCriteriaViewSet, basename='criteria')
router.register(r'analyses', views.AnalysisViewSet, basename='analysis')
router.register(r'visualizations', views.VisualizationViewSet, basename='visualization')
router.register(r'comparisons', views.ReportCompareViewSet, basename='comparison')

urlpatterns = [
    path('', views.index, name='index'),
    path('metadata/', views.DeviceMetadataView.as_view(), name='device-metadata'),
    path('available-dates/', views.AvailableDatesView.as_view(), name='available-dates'),
    path('', include(router.urls)),
]