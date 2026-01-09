from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet, 
    RegisterView, 
    PasswordResetRequestView, 
    PasswordResetConfirmView,
    CustomLoginView,
    TwoFactorVerifyView,
    GroupViewSet,
    GroupInvitationViewSet,
    CreateGroupInvitationView,
    AcceptGroupInvitationView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'group-invitations', GroupInvitationViewSet)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login_obtain_pair'),
    path('login/2fa/', TwoFactorVerifyView.as_view(), name='login_2fa_verify'),
    path('login/refresh/', TokenRefreshView.as_view(), name='login_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('group-invitations/create/', CreateGroupInvitationView.as_view(), name='create_group_invitation'),
    path('group-invitations/accept/', AcceptGroupInvitationView.as_view(), name='accept_group_invitation'),
    path('', include(router.urls)),
]