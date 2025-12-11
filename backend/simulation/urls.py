from django.urls import path

from .views import (
    GenerationHistoryDetail,
    GenerationHistoryListCreate,
    RunGenerationSimulation,
    RunGenerationSimulationRange,
    SimDeviceList,
    TodayForecastEnergy,
    LastMonthEnergy,
    BatteryView,
    MockWeatherRange,
    BatteryHistoryView,
)

urlpatterns = [
    path("devices/", SimDeviceList.as_view()),  # GET /simulation/devices/
    path("generation/run/", RunGenerationSimulation.as_view()),  # POST /simulation/generation/run/
    path("generation/run-range/", RunGenerationSimulationRange.as_view()),  # POST
    path("generation/forecast/today/", TodayForecastEnergy.as_view()),  # GET
    path("generation/forecast/last-month/", LastMonthEnergy.as_view()),  # GET
    path("generation/", GenerationHistoryListCreate.as_view()),  # GET/POST
    path("generation/<int:pk>/", GenerationHistoryDetail.as_view()),  # GET/PATCH/DELETE
    path("battery/", BatteryView.as_view()),  # GET/POST
    path("battery/history/", BatteryHistoryView.as_view()),  # GET
    path("weather/mock/", MockWeatherRange.as_view()),  # GET start/end
]
