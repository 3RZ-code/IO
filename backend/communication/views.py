"""
Views dla modułu communication
Zawiera ViewSety REST API oraz ScheduleManager z logiką biznesową
"""

from typing import List, Optional
from datetime import date

from django.http import HttpResponse
from django.db.models import Q
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, BasePermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Schedule
from .serializers import (
    ScheduleSerializer,
    ScheduleCreateSerializer,
    ScheduleUpdateStatusSerializer
)
from data_acquisition.models import Device
from security.permissions import IsAdmin


class IsAdminOrReadOnly(BasePermission):
    """
    Pozwala na pełny dostęp dla administratorów.
    Użytkownicy mogą tylko odczytywać dane (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        # Dozwolone metody tylko do odczytu dla wszystkich zalogowanych
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        
        # Operacje zapisu tylko dla adminów
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


def index(request):
    return HttpResponse("Communication module!")


# ============================================================================
#                           SCHEDULE MANAGER
# ============================================================================

class ScheduleManager:
    """
    Manager zarządzający operacjami na harmonogramach.
    Implementuje logikę biznesową modułu communication.
    """
    
    # ========== CRUD Operations ==========
    
    @staticmethod
    def save_schedule(schedule: Schedule) -> Schedule:
        """
        Zapisuje harmonogram do bazy danych
        Args:
            schedule: Obiekt Schedule do zapisania
        Returns:
            Zapisany obiekt Schedule
        """
        schedule.save()
        return schedule
    
    @staticmethod
    def find_schedule_by_id(schedule_id: int) -> Optional[Schedule]:
        """
        Znajduje harmonogram po ID
        Args:
            schedule_id: ID harmonogramu
        Returns:
            Obiekt Schedule lub None
        """
        try:
            return Schedule.objects.select_related('device').get(schedule_id=schedule_id)
        except Schedule.DoesNotExist:
            return None
    
    @staticmethod
    def find_schedules_by_user_id(user_id: str) -> List[Schedule]:
        """
        Znajduje wszystkie harmonogramy utworzone przez użytkownika
        Args:
            user_id: ID użytkownika
        Returns:
            Lista harmonogramów
        """
        return list(Schedule.objects.filter(
            user_id=user_id
        ).select_related('device').order_by('-start_date'))
    
    @staticmethod
    def find_schedules_by_device_id(device_id: int) -> List[Schedule]:
        """
        Znajduje wszystkie harmonogramy dla urządzenia
        Args:
            device_id: ID urządzenia
        Returns:
            Lista harmonogramów
        """
        return list(Schedule.objects.filter(
            device__device_id=device_id
        ).select_related('device').order_by('-start_date'))
    
    @staticmethod
    def find_all_schedules() -> List[Schedule]:
        """
        Zwraca wszystkie harmonogramy
        Returns:
            Lista wszystkich harmonogramów
        """
        return list(Schedule.objects.select_related('device').order_by('-start_date'))
    
    @staticmethod
    def find_active_schedules() -> List[Schedule]:
        """
        Zwraca aktywne harmonogramy (working_status=True)
        Returns:
            Lista aktywnych harmonogramów
        """
        return list(Schedule.objects.filter(
            working_status=True
        ).select_related('device').order_by('-start_date'))
    
    @staticmethod
    def find_schedules_by_date_range(start_date: date, end_date: date) -> List[Schedule]:
        """
        Znajduje harmonogramy w zadanym zakresie dat
        Args:
            start_date: Data początkowa
            end_date: Data końcowa
        Returns:
            Lista harmonogramów
        """
        return list(Schedule.objects.filter(
            Q(start_date__lte=end_date) & Q(finish_date__gte=start_date)
        ).select_related('device').order_by('-start_date'))
    
    @staticmethod
    def delete_schedule(schedule_id: int) -> bool:
        """
        Usuwa harmonogram
        Args:
            schedule_id: ID harmonogramu
        Returns:
            True jeśli usunięto, False jeśli nie znaleziono
        """
        try:
            schedule = Schedule.objects.get(schedule_id=schedule_id)
            schedule.delete()
            return True
        except Schedule.DoesNotExist:
            return False
    
    @staticmethod
    def update_schedule_status(schedule_id: int, working_status: bool) -> Optional[Schedule]:
        """
        Aktualizuje status harmonogramu
        Args:
            schedule_id: ID harmonogramu
            working_status: Nowy status
        Returns:
            Zaktualizowany harmonogram lub None
        """
        try:
            schedule = Schedule.objects.get(schedule_id=schedule_id)
            schedule.working_status = working_status
            schedule.save()
            return schedule
        except Schedule.DoesNotExist:
            return None


# ============================================================================
#                           REST API VIEWS
# ============================================================================

class ScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla harmonogramów - obsługuje pełny CRUD
    
    Dostępne endpointy:
    - GET /api/communication/schedules/ - lista harmonogramów
    - POST /api/communication/schedules/ - tworzenie harmonogramu
    - GET /api/communication/schedules/{id}/ - szczegóły harmonogramu
    - PUT /api/communication/schedules/{id}/ - aktualizacja harmonogramu
    - DELETE /api/communication/schedules/{id}/ - usunięcie harmonogramu
    
    Akcje dodatkowe:
    - GET /api/communication/schedules/active/ - aktywne harmonogramy
    - GET /api/communication/schedules/by_user/?user_id=X - harmonogramy użytkownika
    - GET /api/communication/schedules/by_device/?device_id=X - harmonogramy urządzenia
    - GET /api/communication/schedules/by_date_range/?start=X&end=Y - harmonogramy w zakresie dat
    - PATCH /api/communication/schedules/{id}/update_status/ - aktualizacja statusu
    """
    
    queryset = Schedule.objects.select_related('device').all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ScheduleCreateSerializer
        if self.action == 'update_status':
            return ScheduleUpdateStatusSerializer
        return ScheduleSerializer
    
    def get_permissions(self):
        """
        Zwraca odpowiednie uprawnienia w zależności od akcji:
        - list, retrieve, active, by_user, by_device, by_date_range: IsAuthenticated (wszyscy zalogowani)
        - create, update, partial_update, destroy, update_status: IsAdmin (tylko admin)
        """
        if self.action in ['list', 'retrieve', 'active', 'by_user', 'by_device', 'by_date_range']:
            return [IsAuthenticated()]
        return [IsAdmin()]
    
    def list(self, request):
        """Lista wszystkich harmonogramów (dostępne dla wszystkich zalogowanych użytkowników)"""
        schedules = ScheduleManager.find_all_schedules()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Szczegóły harmonogramu (dostępne dla wszystkich zalogowanych użytkowników)"""
        schedule = ScheduleManager.find_schedule_by_id(pk)
        if not schedule:
            return Response(
                {"error": "Harmonogram nie został znaleziony"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data)
    
    def create(self, request):
        """Tworzenie nowego harmonogramu (tylko admin)"""
        serializer = ScheduleCreateSerializer(data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response(
                ScheduleSerializer(schedule).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, pk=None):
        """Aktualizacja harmonogramu (tylko admin)"""
        schedule = ScheduleManager.find_schedule_by_id(pk)
        if not schedule:
            return Response(
                {"error": "Harmonogram nie został znaleziony"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ScheduleCreateSerializer(schedule, data=request.data)
        if serializer.is_valid():
            schedule = serializer.save()
            return Response(ScheduleSerializer(schedule).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """Usunięcie harmonogramu (tylko admin)"""
        if ScheduleManager.delete_schedule(pk):
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Harmonogram nie został znaleziony"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lista aktywnych harmonogramów"""
        schedules = ScheduleManager.find_active_schedules()
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="ID użytkownika",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Lista harmonogramów użytkownika"""
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {"error": "Parametr user_id jest wymagany"},
                status=status.HTTP_400_BAD_REQUEST
            )
        schedules = ScheduleManager.find_schedules_by_user_id(user_id)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'device_id',
                openapi.IN_QUERY,
                description="ID urządzenia",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_device(self, request):
        """Lista harmonogramów urządzenia"""
        device_id = request.query_params.get('device_id')
        if not device_id:
            return Response(
                {"error": "Parametr device_id jest wymagany"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            device_id = int(device_id)
        except ValueError:
            return Response(
                {"error": "device_id musi być liczbą"},
                status=status.HTTP_400_BAD_REQUEST
            )
        schedules = ScheduleManager.find_schedules_by_device_id(device_id)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'start',
                openapi.IN_QUERY,
                description="Data początkowa (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            ),
            openapi.Parameter(
                'end',
                openapi.IN_QUERY,
                description="Data końcowa (YYYY-MM-DD)",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def by_date_range(self, request):
        """Lista harmonogramów w zakresie dat"""
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        
        if not start or not end:
            return Response(
                {"error": "Parametry start i end są wymagane (format: YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start_date = date.fromisoformat(start)
            end_date = date.fromisoformat(end)
        except ValueError:
            return Response(
                {"error": "Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        schedules = ScheduleManager.find_schedules_by_date_range(start_date, end_date)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAdmin])
    def update_status(self, request, pk=None):
        """Aktualizacja statusu harmonogramu (tylko admin)"""
        working_status = request.data.get('working_status')
        
        if working_status is None:
            return Response(
                {"error": "Parametr working_status jest wymagany"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        schedule = ScheduleManager.update_schedule_status(pk, working_status)
        if not schedule:
            return Response(
                {"error": "Harmonogram nie został znaleziony"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data)


# ============================================================================
#                    ALTERNATYWNE WIDOKI (CLASS-BASED VIEWS)
# ============================================================================

# class ScheduleFilter(APIView):
#     """
#     Widok do filtrowania harmonogramów (dostępny dla wszystkich zalogowanych)
#     GET /api/communication/schedules-filter/
    
#     Parametry query:
#     - device_id: ID urządzenia
#     - user_id: ID użytkownika
#     - working_status: status (true/false)
#     - start_date: data początkowa (YYYY-MM-DD)
#     - end_date: data końcowa (YYYY-MM-DD)
#     """
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         device_id = request.GET.get("device_id")
#         user_id = request.GET.get("user_id")
#         working_status = request.GET.get("working_status")
#         start_date = request.GET.get("start_date")
#         end_date = request.GET.get("end_date")
        
#         schedules = Schedule.objects.select_related('device').all()
        
#         if device_id:
#             try:
#                 schedules = schedules.filter(device__device_id=int(device_id))
#             except ValueError:
#                 return Response(
#                     {"error": "device_id musi być liczbą"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
        
#         if user_id:
#             schedules = schedules.filter(user_id=user_id)
        
#         if working_status is not None:
#             if working_status.lower() in ['true', '1', 'yes']:
#                 schedules = schedules.filter(working_status=True)
#             elif working_status.lower() in ['false', '0', 'no']:
#                 schedules = schedules.filter(working_status=False)
        
#         if start_date:
#             try:
#                 start = date.fromisoformat(start_date)
#                 schedules = schedules.filter(start_date__gte=start)
#             except ValueError:
#                 return Response(
#                     {"error": "Nieprawidłowy format start_date. Użyj YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
        
#         if end_date:
#             try:
#                 end = date.fromisoformat(end_date)
#                 schedules = schedules.filter(finish_date__lte=end)
#             except ValueError:
#                 return Response(
#                     {"error": "Nieprawidłowy format end_date. Użyj YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
        
#         serializer = ScheduleSerializer(schedules, many=True)
#         return Response(serializer.data)