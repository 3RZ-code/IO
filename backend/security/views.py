
from rest_framework import viewsets, permissions, generics, decorators, response, status
from .models import User, Code, GroupInvitation
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    CustomTokenObtainPairSerializer,
    TwoFactorVerifySerializer,
    GroupSerializer,
    GroupInvitationSerializer,
    CreateGroupInvitationSerializer,
    AcceptGroupInvitationSerializer
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
        
        try:
            subject = 'Witamy w Systemie!'
            html_content = render_to_string('security/registration_email.html', {'user': user})
            text_content = f"Witaj {user.username},\n\nDziękujemy za rejestrację w naszym systemie."
            
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
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
            
            code = ''.join(random.choices(string.digits, k=6))
            
            Code.objects.create(user=user, code=code, purpose='RESET_PASSWORD')
            
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
            
            code_obj = Code.objects.filter(
                user=user, 
                code=code, 
                purpose='RESET_PASSWORD'
            ).order_by('-created_at').first()

            if not code_obj:
                return response.Response({"error": "Invalid code"}, status=400)
                
            if timezone.now() - code_obj.created_at > datetime.timedelta(minutes=15):
                 return response.Response({"error": "Code expired"}, status=400)
                 
            user.set_password(new_password)
            user.save()
            
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
            
            # Sprawdź, czy istnieje już aktywny kod utworzony w ciągu ostatniej minuty
            recent_code = Code.objects.filter(
                user=user,
                purpose='TWO_FACTOR',
                created_at__gte=timezone.now() - datetime.timedelta(minutes=1)
            ).order_by('-created_at').first()
            
            if recent_code:
                # Użyj istniejącego kodu, nie wysyłaj emaila ponownie
                code = recent_code.code
            else:
                # Utwórz nowy kod i wyślij email tylko raz
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
            
            code_obj = Code.objects.filter(
                user=user, 
                code=code, 
                purpose='TWO_FACTOR'
            ).order_by('-created_at').first()

            if not code_obj:
                return response.Response({"error": "Invalid code"}, status=400)
                
            if timezone.now() - code_obj.created_at > datetime.timedelta(minutes=15):
                 return response.Response({"error": "Code expired"}, status=400)
            
            code_obj.delete()
            
            refresh = RefreshToken.for_user(user)
            
            return response.Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
            
        except User.DoesNotExist:
             return response.Response({"error": "Invalid user"}, status=400)

class GroupInvitationViewSet(viewsets.ModelViewSet):
    queryset = GroupInvitation.objects.all()
    serializer_class = GroupInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        return GroupInvitation.objects.all()

class CreateGroupInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    serializer_class = CreateGroupInvitationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        group_id = serializer.validated_data['group_id']
        email = serializer.validated_data['email']
        
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return response.Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        while GroupInvitation.objects.filter(code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        invitation = GroupInvitation.objects.create(
            group=group,
            email=email,
            code=code,
            created_by=request.user
        )
        
        try:
            subject = f'Zaproszenie do grupy {group.name}'
            context = {
                'group_name': group.name,
                'code': code,
                'invited_by': request.user.username,
                'email': email
            }
            
            html_content = render_to_string('security/group_invitation_email.html', context)
            text_content = f"""
Witaj,

Zostałeś zaproszony do grupy "{group.name}" przez użytkownika {request.user.username}.

Twój kod zaproszenia to: {code}

Kod jest ważny przez 7 dni. Użyj go, aby dołączyć do grupy.

Pozdrawiamy,
System
            """
            
            msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            
            return response.Response({
                "message": "Invitation created and sent successfully",
                "invitation": GroupInvitationSerializer(invitation).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Failed to send invitation email: {e}")
            return response.Response({
                "message": "Invitation created but email failed to send",
                "invitation": GroupInvitationSerializer(invitation).data,
                "warning": "Email could not be sent"
            }, status=status.HTTP_201_CREATED)

class AcceptGroupInvitationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AcceptGroupInvitationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        user = request.user
        
        try:
            invitation = GroupInvitation.objects.get(code=code, used=False)
        except GroupInvitation.DoesNotExist:
            return response.Response(
                {"error": "Invalid or already used invitation code"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invitation.email.lower() != user.email.lower():
            return response.Response(
                {"error": "This invitation was sent to a different email address"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if timezone.now() - invitation.created_at > datetime.timedelta(days=7):
            return response.Response(
                {"error": "Invitation code has expired"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitation.group.user_set.add(user)
        
        invitation.used = True
        invitation.used_at = timezone.now()
        invitation.used_by = user
        invitation.save()
        
        return response.Response({
            "message": f"Successfully joined group '{invitation.group.name}'",
            "group": GroupSerializer(invitation.group).data
        }, status=status.HTTP_200_OK)
