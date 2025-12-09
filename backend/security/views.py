
from rest_framework import viewsets, permissions, generics, decorators, response, status
from .models import User, Code
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
    TwoFactorVerifySerializer,
    GroupSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import random
import string
import datetime
from .permissions import IsAdmin, IsOwnerOrAdmin
from django.contrib.auth.models import Group

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        return super().get_permissions()

    @decorators.action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        
        # Send welcome email
        try:
            subject = 'Witamy w Systemie!'
            html_content = render_to_string('security/registration_email.html', {'user': user})
            text_content = f"Witaj {user.username},\n\nDziękujemy za rejestrację w naszym systemie."
            
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to send email: {e}")

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate 6-digit code
            code = ''.join(random.choices(string.digits, k=6))
            
            # Create Code object
            Code.objects.create(user=user, code=code, purpose='RESET_PASSWORD')
            
            # Send email
            try:
                subject = 'Resetowanie Hasła'
                html_content = render_to_string('security/password_reset_email.html', {'user': user, 'code': code})
                text_content = f"Twój kod resetowania hasła to: {code}"
                
                msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                print(f"Failed to send reset email: {e}")
                
            return response.Response({"message": "Password reset code sent if email exists."})
            
        except User.DoesNotExist:
            # Don't reveal user existence
            return response.Response({"message": "Password reset code sent if email exists."})

class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(email=email)
            
            # Verify code
            code_obj = Code.objects.filter(
                user=user, 
                code=code, 
                purpose='RESET_PASSWORD'
            ).order_by('-created_at').first()

            if not code_obj:
                return response.Response({"error": "Invalid code"}, status=400)
                
            # Verify expiry (15 minutes)
            if timezone.now() - code_obj.created_at > datetime.timedelta(minutes=15):
                 return response.Response({"error": "Code expired"}, status=400)
                 
            # Reset password
            user.set_password(new_password)
            user.save()
            
            # Invalidate code (and potentially older ones)
            code_obj.delete()
            
            return response.Response({"message": "Password has been reset successfully."})
            
        except User.DoesNotExist:
             return response.Response({"error": "Invalid data"}, status=400)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        
        if data.get('2fa_required'):
            user = serializer.user
            
            # Generate and send code
            code = ''.join(random.choices(string.digits, k=6))
            Code.objects.create(user=user, code=code, purpose='TWO_FACTOR')
            
            try:
                subject = 'Weryfikacja Dwuetapowa'
                html_content = render_to_string('security/2fa_email.html', {'user': user, 'code': code})
                text_content = f"Twój kod weryfikacyjny to: {code}"
                
                msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except Exception as e:
                print(f"Failed to send 2FA email: {e}")
                
            return response.Response(data, status=status.HTTP_200_OK)
            
        return response.Response(data, status=status.HTTP_200_OK)

class TwoFactorVerifyView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = TwoFactorVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        code = serializer.validated_data['code']
        
        try:
            user = User.objects.get(id=user_id)
            
            # Verify code
            code_obj = Code.objects.filter(
                user=user, 
                code=code, 
                purpose='TWO_FACTOR'
            ).order_by('-created_at').first()

            if not code_obj:
                return response.Response({"error": "Invalid code"}, status=400)
                
            # Verify expiry (15 minutes)
            if timezone.now() - code_obj.created_at > datetime.timedelta(minutes=15):
                 return response.Response({"error": "Code expired"}, status=400)
            
            # Code valid, generate tokens
            code_obj.delete()
            
            refresh = RefreshToken.for_user(user)
            
            return response.Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
            
        except User.DoesNotExist:
             return response.Response({"error": "Invalid user"}, status=400)
