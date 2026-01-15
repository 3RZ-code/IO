from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q
from security.permissions import IsAdmin
from .models import Alert, Notification, NotificationPreferences
from .serializers import AlertSerializer, NotificationSerializer, NotificationPreferencesSerializer


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAdmin]  # CRUD tylko dla admina
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'confirm', 'mute', 'my_alerts', 'statistics']:
            return [IsAuthenticated()]
        return super().get_permissions()


    def get_queryset(self):
        user = self.request.user
        
        if user.is_authenticated and hasattr(user, 'role') and user.role == 'admin':
            queryset = Alert.objects.all()
        elif user.is_authenticated:
            queryset = Alert.objects.filter(Q(user=user) | Q(user__isnull=True))
        else:
            queryset = Alert.objects.none()
        
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
        """
        Tworzy nowy alert. Ustawia właściciela jeśli nie podano.
        Powiadomienia są obsługiwane automatycznie przez signals.py.
        """
        if 'user' not in serializer.validated_data or serializer.validated_data.get('user') is None:
            alert = serializer.save(user=self.request.user)
        else:
            alert = serializer.save()
        # Powiadomienia tworzy signals.handle_alert_notifications automatycznie

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """
        Potwierdza alert (zmienia status na CONFIRMED).
        Powiadomienia o potwierdzeniu są obsługiwane przez signals.py.
        """
        alert = self.get_object()
        alert.confirmAlert()
        # Powiadomienia tworzy signals.handle_confirmation_notifications automatycznie
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mute(self, request, pk=None):
        alert = self.get_object()
        alert.muteAlert()
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_alerts(self, request):
        if not request.user.is_authenticated:
            return Response({'message': 'No alerts for anonymous users', 'results': []})
        
        alerts = Alert.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = Alert.objects.all() if (hasattr(user, 'role') and user.role == 'admin') else Alert.objects.filter(user=user)
        
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

    def _send_confirmation_notifications(self, alert, confirmed_by):
        from security.models import User
        import pytz
        
        recipients = set()  
        
        if alert.user and alert.user != confirmed_by:
            recipients.add(alert.user)
        
        admins = User.objects.filter(role='admin')
        for admin in admins:
            recipients.add(admin)
        
        local_tz = pytz.timezone('Europe/Warsaw')
        current_time = timezone.now().astimezone(local_tz).time()
        
        for user in recipients:
            preferences = NotificationPreferences.objects.filter(user=user).first()
            

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        queryset = Notification.objects.filter(user=user)
        
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
            
        return queryset.order_by('-sent_at')

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.markAsRead()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        count = notifications.count()
        notifications.update(is_read=True)
        return Response({'marked_as_read': count})

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        if not request.user.is_authenticated:
            return Response({'unread_count': 0})
        
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class NotificationPreferencesViewSet(viewsets.ModelViewSet):
    queryset = NotificationPreferences.objects.all()
    serializer_class = NotificationPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return NotificationPreferences.objects.all()
        return NotificationPreferences.objects.filter(user=user)

    @action(detail=False, methods=['get', 'post', 'put'])
    def my_preferences(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
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
