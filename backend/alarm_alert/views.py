from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from .models import Alert, Notification, NotificationPreferences
from .serializers import AlertSerializer, NotificationSerializer, NotificationPreferencesSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla zarządzania alertami.
    Obsługuje CRUD oraz dodatkowe akcje: confirm, mute.
    """
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtruje alerty w zależności od roli użytkownika"""
        user = self.request.user
        queryset = Alert.objects.all()
        
        # Filtruj według użytkownika jeśli nie jest adminem
        if user.role != 'admin':
            queryset = queryset.filter(Q(user=user) | Q(user__isnull=True))
        
        # Parametry filtrowania
        severity = self.request.query_params.get('severity')
        status_filter = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        
        if severity:
            queryset = queryset.filter(severity=severity)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if category:
            queryset = queryset.filter(category=category)
            
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Tworzy alert i powiadomienie dla użytkownika"""
        alert = serializer.save()
        
        # Utwórz powiadomienie dla użytkownika
        if alert.user:
            self._create_notification_for_alert(alert)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Potwierdza alert"""
        alert = self.get_object()
        alert.confirmAlert()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mute(self, request, pk=None):
        """Wycisza alert"""
        alert = self.get_object()
        alert.muteAlert()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_alerts(self, request):
        """Zwraca alerty zalogowanego użytkownika"""
        alerts = Alert.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Zwraca statystyki alertów"""
        user = request.user
        queryset = Alert.objects.all() if user.role == 'admin' else Alert.objects.filter(user=user)
        
        stats = {
            'total': queryset.count(),
            'by_severity': {
                'CRITICAL': queryset.filter(severity='CRITICAL').count(),
                'WARNING': queryset.filter(severity='WARNING').count(),
                'INFO': queryset.filter(severity='INFO').count(),
            },
            'by_status': {
                'NEW': queryset.filter(status='NEW').count(),
                'CONFIRMED': queryset.filter(status='CONFIRMED').count(),
                'MUTED': queryset.filter(status='MUTED').count(),
                'CLOSED': queryset.filter(status='CLOSED').count(),
            },
            'muted_count': queryset.filter(is_muted=True).count(),
        }
        return Response(stats)

    def _create_notification_for_alert(self, alert):
        """Pomocnicza metoda do tworzenia powiadomienia"""
        # Sprawdź preferencje użytkownika
        preferences = NotificationPreferences.objects.filter(user=alert.user).first()
        
        if preferences and not preferences.is_active:
            return
        
        # Sprawdź godziny ciszy
        if preferences and preferences.quiet_hours_start and preferences.quiet_hours_end:
            current_time = timezone.now().time()
            if preferences.quiet_hours_start <= current_time <= preferences.quiet_hours_end:
                return
        
        # Utwórz powiadomienie
        Notification.objects.create(
            user=alert.user,
            alert=alert,
            message=f"[{alert.severity}] {alert.title}: {alert.description}"
        )


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla zarządzania powiadomieniami.
    Obsługuje CRUD oraz akcję mark_as_read.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Zwraca tylko powiadomienia zalogowanego użytkownika"""
        user = self.request.user
        queryset = Notification.objects.filter(user=user)
        
        # Parametry filtrowania
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
            
        return queryset.order_by('-sent_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Oznacza powiadomienie jako przeczytane"""
        notification = self.get_object()
        notification.markAsRead()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Oznacza wszystkie powiadomienia użytkownika jako przeczytane"""
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({'marked_as_read': count})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Zwraca liczbę nieprzeczytanych powiadomień"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class NotificationPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla zarządzania preferencjami powiadomień.
    """
    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Zwraca tylko preferencje zalogowanego użytkownika"""
        user = self.request.user
        if user.role == 'admin':
            return NotificationPreferences.objects.all()
        return NotificationPreferences.objects.filter(user=user)

    @action(detail=False, methods=['get', 'post', 'put'])
    def my_preferences(self, request):
        """Zwraca lub aktualizuje preferencje zalogowanego użytkownika"""
        preferences, created = NotificationPreferences.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = self.get_serializer(preferences)
            return Response(serializer.data)
        
        elif request.method in ['POST', 'PUT']:
            serializer = self.get_serializer(preferences, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_quiet_hours(self, request, pk=None):
        """Ustawia godziny ciszy"""
        preferences = self.get_object()
        start_time = request.data.get('quiet_hours_start')
        end_time = request.data.get('quiet_hours_end')
        
        if not start_time or not end_time:
            return Response(
                {'error': 'Both quiet_hours_start and quiet_hours_end are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        preferences.setQuietHours(start_time, end_time)
        serializer = self.get_serializer(preferences)
        return Response(serializer.data)
