from rest_framework import serializers
from .models import User, Code, GroupInvitation
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import Group

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Group.objects.all(), source='groups', required=False
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'birth_date', 'google_id', 'created_at', 'updated_at', 'terms_accepted', 'privacy_policy_accepted', 'two_factor_enabled', 'groups', 'group_ids']
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'terms_accepted', 'privacy_policy_accepted']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            terms_accepted=validated_data.get('terms_accepted', False),
            privacy_policy_accepted=validated_data.get('privacy_policy_accepted', False)
        )
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        if self.user.two_factor_enabled:
            return {
                '2fa_required': True,
                'user_id': self.user.id
            }
        
        return data

class TwoFactorVerifySerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    code = serializers.CharField(max_length=6)

class GroupInvitationSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source='group.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    used_by_name = serializers.CharField(source='used_by.username', read_only=True)

    class Meta:
        model = GroupInvitation
        fields = ['id', 'group', 'group_name', 'email', 'code', 'created_by', 'created_by_name', 
                  'created_at', 'used', 'used_at', 'used_by', 'used_by_name']
        read_only_fields = ['id', 'code', 'created_by', 'created_at', 'used', 'used_at', 'used_by']

class CreateGroupInvitationSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    email = serializers.EmailField()

class AcceptGroupInvitationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)
